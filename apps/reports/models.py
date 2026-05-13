from django.db import models
from apps.users.models import User


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Генерируется"
        DONE = "done", "Готов"
        ERROR = "error", "Ошибка"

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="Создан пользователем"
    )
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
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"