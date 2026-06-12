# serializers.py
from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    file_url = serializers.SerializerMethodField()
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    filter_display = serializers.CharField(source="get_filter_display", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "title",
            "status",
            "file_url",
            "error_message",
            "created_by_name",
            "created_at",
            "date_from",
            "date_to",
            "severity",
            "severity_display",
            "filter_display",
        ]
        read_only_fields = [
            "id", "status", "file_url", "error_message", "created_at",
            "severity_display", "filter_display"
        ]

    def get_file_url(self, obj) -> str | None:
        if obj.file:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None


# ==================== СЕРИАЛАЙЗЕР ДЛЯ ГЕНЕРАЦИИ ====================
class ReportGenerateSerializer(serializers.Serializer):
    """Сериализатор специально для создания отчёта (POST /generate/)"""

    date_from = serializers.DateField(
        required=False,
        help_text="Начальная дата (YYYY-MM-DD)"
    )
    date_to = serializers.DateField(
        required=False,
        help_text="Конечная дата (YYYY-MM-DD)"
    )
    severity = serializers.ChoiceField(
        choices=Report.SeverityFilter.choices,
        default=Report.SeverityFilter.ALL,
        help_text="Уровень серьёзности"
    )

    def validate(self, attrs):
        if attrs.get('date_from') and attrs.get('date_to'):
            if attrs['date_from'] > attrs['date_to']:
                raise serializers.ValidationError("date_from не может быть позже date_to")
        return attrs