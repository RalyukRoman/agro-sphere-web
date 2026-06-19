from django.db import models
from django.contrib.gis.db import models
from users.models import Company
import uuid


class Field(models.Model):
    """Модель для представлення поля."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    company = models.ForeignKey(
        verbose_name="Компанія",
        to=Company, 
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name="Назва",
        max_length=100
    )

    geom = models.PolygonField(
        verbose_name="Координати меж поля"
    )

    area_hectares = models.FloatField(
        verbose_name="Площа (га)",
        blank=True, 
        null=True
    )

    class CropStatusChoice(models.TextChoices):
        PLANNED = "PLANNED", "Заплановано"
        SOWN = "SOWN", "Посіяно"
        GERMINATED = "GERMINATED", "Сходи (Проростання)"
        GROWING = "GROWING", "Вегетація (Росте)"
        FLOWERING = "FLOWERING", "Цвітіння"
        RIPENING = "RIPENING", "Дозрівання"
        READY = "READY", "Готово до збору"
        HARVESTED = "HARVESTED", "Зібрано"
        FAILED = "FAILED", "Втрачено (Загинуло)"

    crop_status = models.CharField(
        verbose_name="Статус",
        max_length=15,
        choices=CropStatusChoice.choices,
        default=CropStatusChoice.PLANNED,
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.geom:
            geom_projected = self.geom.transform(3857, clone=True)
            self.area_hectares = round(geom_projected.area / 10000, 2)
        super().save(*args, **kwargs)