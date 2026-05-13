from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer
from .tasks import generate_report_task


class ReportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET    /reports/              — список отчётов
    GET    /reports/{id}/         — детально
    DELETE /reports/{id}/         — удалить
    POST   /reports/generate/     — сгенерировать новый PDF
    """
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        # Фильтры из тела запроса
        filters = {}

        date_from = request.data.get("date_from")
        date_to = request.data.get("date_to")
        severity = request.data.get("severity")
        source_type = request.data.get("source_type")

        if date_from:
            filters["created_at__date__gte"] = date_from
        if date_to:
            filters["created_at__date__lte"] = date_to
        if severity:
            filters["severity"] = severity
        if source_type:
            filters["source_type"] = source_type

        report = Report.objects.create(
            title=f"Отчёт по дефектам",
            created_by=request.user,
        )
        # Передаём фильтры в таск
        generate_report_task.delay(report.id, filters)

        serializer = ReportSerializer(report, context={"request": request})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)