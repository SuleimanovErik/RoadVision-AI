# apps/reports/views.py
from rest_framework import mixins, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import IsAdmin

from .models import Report
from .serializers import ReportSerializer, ReportGenerateSerializer
from .tasks import generate_report_task


class ReportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]   # ← Только Администратор
    serializer_class = ReportSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'severity']

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Формируем красивый заголовок
        title = "Отчёт по дефектам"
        if data.get('severity') and data['severity'] != "all":
            title += f" — {data['severity'].upper()}"
        if data.get('date_from') or data.get('date_to'):
            title += f" ({data.get('date_from') or '...'} — {data.get('date_to') or '...'})"

        report = Report.objects.create(
            title=title,
            created_by=request.user,
            date_from=data.get('date_from'),
            date_to=data.get('date_to'),
            severity=data.get('severity', 'all'),
        )

        filters = {}
        if data.get('date_from'):
            filters["created_at__date__gte"] = data['date_from']
        if data.get('date_to'):
            filters["created_at__date__lte"] = data['date_to']
        if data.get('severity') and data['severity'] != "all":
            if data['severity'] == "confirmed":
                filters["status"] = "confirmed"
            else:
                filters["severity"] = data['severity']

        generate_report_task.delay(report.id, filters)

        output_serializer = ReportSerializer(report, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_202_ACCEPTED)