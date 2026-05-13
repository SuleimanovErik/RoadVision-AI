from django.db import models
from django.utils import timezone
from apps.cameras.models import Camera


class StreamSession(models.Model):

    class Status(models.TextChoices):
        IDLE = "idle", "Ожидание"
        RUNNING = "running", "Запущен"
        ERROR = "error", "Ошибка"
        STOPPED = "stopped", "Остановлен"

    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Камера",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IDLE,
        db_index=True,
        verbose_name="Статус",
    )
    is_active = models.BooleanField(default=False, verbose_name="Активен")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Запущен в")
    stopped_at = models.DateTimeField(null=True, blank=True, verbose_name="Остановлен в")
    last_active = models.DateTimeField(null=True, blank=True, verbose_name="Последняя активность")
    fps = models.FloatField(null=True, blank=True, verbose_name="FPS")
    resolution = models.CharField(max_length=50, null=True, blank=True, verbose_name="Разрешение")
    error_message = models.TextField(blank=True, default="", verbose_name="Ошибка")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Сессия стриминга"
        verbose_name_plural = "Сессии стриминга"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_active"]),
            models.Index(fields=["camera", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.camera.name} — {self.get_status_display()}"

    @property
    def duration_seconds(self) -> float | None:
        if not self.started_at:
            return None
        end = self.stopped_at or timezone.now()
        return (end - self.started_at).total_seconds()

    def mark_running(self) -> None:
        self.status = self.Status.RUNNING
        self.is_active = True
        self.started_at = timezone.now()
        self.error_message = ""
        self.save(update_fields=["status", "is_active", "started_at", "error_message"])

    def mark_stopped(self) -> None:
        self.status = self.Status.STOPPED
        self.is_active = False
        self.stopped_at = timezone.now()
        self.save(update_fields=["status", "is_active", "stopped_at"])

    def mark_error(self, message: str = "") -> None:
        self.status = self.Status.ERROR
        self.is_active = False
        self.error_message = message
        self.save(update_fields=["status", "is_active", "error_message"])

    def ping(self) -> None:
        self.last_active = timezone.now()
        self.save(update_fields=["last_active"])