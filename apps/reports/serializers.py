from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id", "title", "status", "file_url",
            "error_message", "created_by_name", "created_at",
        ]
        read_only_fields = ["id", "status", "file_url", "error_message", "created_at"]

    def get_file_url(self, obj) -> str | None:
        if obj.file:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.file.url) if request else obj.file.url
        return None