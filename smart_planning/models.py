from django.db import models
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError

from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator
)

from geo_analytics.models import Field
from decimal import Decimal
import uuid


class CropCulture(models.Model):
    """Модель для преставлення сільськогосподарської культури."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    name = models.CharField(max_length=100)

    optimal_moisture_min = models.FloatField(
        verbose_name="Мінімальна вологість",
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

    optimal_moisture_max = models.FloatField(
        verbose_name="Максимальна вологість",
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ]
    )

    optimal_temp_min = models.FloatField(
        verbose_name="Мінімальна температура",
        validators=[
            MinValueValidator(-100.0),
            MaxValueValidator(100.0)
        ]
    )

    optimal_temp_max = models.FloatField(
        verbose_name="Максимальна температура",
        validators=[
            MinValueValidator(-100.0),
            MaxValueValidator(100.0)
        ]
    )

    average_yield_per_ha = models.FloatField(
        verbose_name="Середня врожайність",
        validators=[
            MinValueValidator(0.01)
        ]
    )

    base_market_price = models.DecimalField(
        verbose_name="Базова ціна на ринку",
        max_digits=10, 
        decimal_places=2, 
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(optimal_temp_max__gte=models.F("optimal_temp_min")),
                name="max_temp_gte_min_temp",
            ),

            models.CheckConstraint(
                check=models.Q(optimal_moisture_max__gte=models.F("optimal_moisture_min")),
                name="max_moisture_gte_min_moisture",
            )
        ]
    
    def clean(self):
        try:
            self.clean_fields()
        except ValidationError as e:
            errors = e.update_error_dict({})
        else:
            errors = {}

        if (
            self.optimal_temp_min is not None
            and self.optimal_temp_max is not None
        ):
            if self.optimal_temp_max < self.optimal_temp_min:
                errors["optimal_temp_max"] = (
                    "Максимальна температура не може бути меншою за мінімальну."
                )

        if (
            self.optimal_moisture_min is not None
            and self.optimal_moisture_max is not None
        ):
            if self.optimal_moisture_max < self.optimal_moisture_min:
                errors["optimal_moisture_max"] = (
                    "Максимальна вологість не може бути меншою за мінімальну."
                )

        if errors:
            raise ValidationError(errors)
    
    def __str__(self):
        return self.name
    

class CropPlan(models.Model):
    """Модель для представлення згенерованого плану посіву."""

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

    suggested_crop = models.ForeignKey(
        verbose_name="Рекомендована культура",
        to=CropCulture, 
        on_delete=models.CASCADE
    )

    confidence_score = models.FloatField(
        verbose_name="Коефіцієнт впевненості",
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )

    expected_yield = models.FloatField(
        verbose_name="Очікувана врожайність",
        validators=[
            MinValueValidator(0.01)
        ]
    )

    estimated_profit = models.DecimalField(
        verbose_name="Очікувана чиста вартість",
        max_digits=10, 
        decimal_places=2, 
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    created_at = models.DateTimeField(
        verbose_name="Дата створення",
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.field.name} - {self.suggested_crop.name}"