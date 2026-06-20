from django.db import models
from django.contrib.gis.db import models

from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator
)

from geo_analytics.models import Company, Field
from smart_planning.models import CropCulture
import uuid


class Warehouse(models.Model):
    """Модель для представлення складів."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    company = models.ForeignKey(
        verbose_name="Компанія",
        to=Company, 
        on_delete=models.CASCADE
    )
    
    name = models.CharField(
        verbose_name="Назва",
        max_length=100
    )

    location = models.PointField(
        verbose_name="Координати"
    )

    capacity_tons = models.FloatField(
        verbose_name="Вместимість",
        validators=[
            MinValueValidator(0.01)
        ]
    )

    current_balance_tons = models.FloatField(
        verbose_name="Поточний баланс",
        validators=[
            MinValueValidator(0.0)
        ]
    )

    @property
    def fill_percentage(self):
        if self.capacity_tons and self.capacity_tons > 0:
            percentage = (self.current_balance_tons / self.capacity_tons) * 100
            return min(round(percentage, 1), 100.0)
        return 0.0
    
    @property
    def recent_transactions(self):
        return self.transactions.all().order_by('-created_at')[:3]

    def __str__(self):
        return self.name


class GrainBatch(models.Model):
    """Модель для представлення партії зерна."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    field = models.ForeignKey(
        verbose_name="Поле",
        to=Field, 
        on_delete=models.CASCADE
    )

    crop_type = models.ForeignKey(
        verbose_name="Тип культури",
        to=CropCulture, 
        on_delete=models.CASCADE
    )

    grain_class = models.PositiveIntegerField(
        verbose_name="Клас зерна",
        validators=[
            MinValueValidator(1)
        ]
    )
    
    moisture = models.FloatField(
        verbose_name="Вологість",
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

    def __str__(self):
        return f"{self.field.name} - Batch {self.grain_class}"
    

class WarehouseJournalEntry(models.Model):
    """Модель для представлення транзакційний журнал обліку."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    warehouse = models.ForeignKey(
        verbose_name="Склад",
        to=Warehouse, 
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    batch = models.ForeignKey(
        verbose_name="Партія",
        to=GrainBatch, 
        on_delete=models.CASCADE
    )

    class EntryTypeChoice(models.TextChoices):
        INCOMING = "INCOMING", "Надходження"
        OUTGOING = "OUTGOING", "Списання/відвантаження"
        RESERVED = "RESERVED", "Бронювання під логістику"
    
    entry_type = models.CharField(
        verbose_name="Тип операції",
        max_length=15,
        choices=EntryTypeChoice.choices,
        default=EntryTypeChoice.INCOMING,
    )   

    weight_tons = models.FloatField(
        verbose_name="Вага (тонна)",
        validators=[
            MinValueValidator(0.01)
        ]
    )

    created_at = models.DateTimeField(
        verbose_name="Час створення",
        auto_now_add=True
    )

    operator_id = models.UUIDField(
        verbose_name="ID оператора"
    )

    def __str__(self):
        return f"{self.warehouse.name} - {self.entry_type}"
    