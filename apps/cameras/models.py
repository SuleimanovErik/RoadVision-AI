from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Camera(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "active", _("Активна")
        INACTIVE = "inactive", _("Неактивна")
        MAINTENANCE = "maintenance", _("Обслуживание")
        ERROR = "error", _("Ошибка")

    # Основная информация
    name = models.CharField(
        max_length=255,
        verbose_name=_("Название"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Описание"),
    )
    rtsp_url = models.URLField(
        max_length=500,
        verbose_name=_("RTSP URL"),
        help_text=_("Пример: rtsp://user:pass@192.168.1.1:554/stream"),
    )

    # Геолокация
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Широта"),
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90),
        ],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Долгота"),
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180),
        ],
    )
    location_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Адрес установки"),
    )

    # Статус
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Статус"),
        db_index=True,
    )
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Последняя активность"),
    )

    # is_active оставляем для обратной совместимости
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активна"),
    )

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создана"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлена"))

    class Meta:
        verbose_name = _("Камера")
        verbose_name_plural = _("Камеры")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["status", "name"]),
            models.Index(fields=["latitude", "longitude"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_status_display()})"

    def __repr__(self) -> str:
        return f"<Camera id={self.pk} name={self.name!r} status={self.status!r}>"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def coordinates(self) -> tuple:
        """Возвращает (latitude, longitude) как float."""
        return float(self.latitude), float(self.longitude)

    @property
    def is_online(self) -> bool:
        """Камера онлайн если активна и статус ACTIVE."""
        return self.is_active and self.status == self.Status.ACTIVE

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def mark_online(self) -> None:
        """Фиксирует успешное соединение."""
        from django.utils import timezone

        self.status = self.Status.ACTIVE
        self.is_active = True
        self.last_seen_at = timezone.now()
        self.save(update_fields=["status", "is_active", "last_seen_at", "updated_at"])

    def mark_error(self) -> None:
        """Переводит камеру в статус ошибки."""
        self.status = self.Status.ERROR
        self.save(update_fields=["status", "updated_at"])

    def deactivate(self) -> None:
        """Полностью отключает камеру."""
        self.status = self.Status.INACTIVE
        self.is_active = False
        self.save(update_fields=["status", "is_active", "updated_at"])