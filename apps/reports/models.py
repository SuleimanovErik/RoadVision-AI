# models.py
from django.db import models
from apps.users.models import User


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Генерируется"
        DONE = "done", "Готов"
        ERROR = "error", "Ошибка"

    class SeverityFilter(models.TextChoices):
        ALL = "all", "Все"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"
        CONFIRMED = "confirmed", "Confirmed only"

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Создан пользователем"
    )

    # === Новые поля для хранения фильтров ===
    date_from = models.DateField(null=True, blank=True, verbose_name="С даты")
    date_to = models.DateField(null=True, blank=True, verbose_name="По дату")
    severity = models.CharField(
        max_length=20,
        choices=SeverityFilter.choices,
        default=SeverityFilter.ALL,
        verbose_name="Уровень критичности"
    )
    # source_type можно добавить позже, если нужно

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    file = models.FileField(
        upload_to="reports/", null=True, blank=True, verbose_name="PDF файл"
    )
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"
        ordering = ["-created_at"]  # <-- новые всегда сверху

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_filter_display(self):
        parts = []
        if self.date_from or self.date_to:
            parts.append(f"{self.date_from or '…'} — {self.date_to or '…'}")
        if self.severity != self.SeverityFilter.ALL:
            parts.append(self.get_severity_display())
        return " | ".join(parts) or "Все дефекты"