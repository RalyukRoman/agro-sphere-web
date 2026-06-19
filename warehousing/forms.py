from django import forms
from django.db import transaction
from django.contrib.gis import forms as gis_forms
from django.core.exceptions import ValidationError
from geo_analytics.models import Field
from smart_planning.models import CropCulture

from .models import (
    Warehouse, 
    GrainBatch, 
    WarehouseJournalEntry
)

from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator
)


class WarehouseForm(gis_forms.ModelForm):
    """Форма для реєстрації складу з вказанням точки на карті."""

    class Meta:
        model = Warehouse
        fields = [
            'name', 'capacity_tons', 
            'current_balance_tons', 'location'
        ]
        widgets = {
            'location': gis_forms.OSMWidget(attrs={
                'default_lat': 49.0,
                'default_lon': 31.0,
            }),
 
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'capacity_tons': forms.NumberInput(attrs={
                'class': 'form-control'
            }),

            'current_balance_tons': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class GrainIncomingForm(forms.Form):
    """Форма для одночасного створення партії та запису в журнал складу."""
    
    # --- GrainBatch ---
    field = forms.ModelChoiceField(
        queryset=Field.objects.all(),
        label="Поле походження",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    crop_type = forms.ModelChoiceField(
        queryset=CropCulture.objects.all(),
        label="Тип культури",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    grain_class = forms.IntegerField(
        label="Клас зерна",
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'min': 1
        })
    )

    moisture = forms.FloatField(
        label="Вологість (%)",
        validators=[
            MinValueValidator(0.0), 
            MaxValueValidator(100.0)
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'step': '0.1'
        })
    )

    # --- WarehouseJournalEntry ---
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label="Склад прийому",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    weight_tons = forms.FloatField(
        label="Вага (тонн)",
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'step': '0.01'
        })
    )

    def save(self, operator):
        with transaction.atomic():
            batch = GrainBatch.objects.create(
                field=self.cleaned_data['field'],
                crop_type=self.cleaned_data['crop_type'],
                grain_class=self.cleaned_data['grain_class'],
                moisture=self.cleaned_data['moisture']
            )

            journal_entry = WarehouseJournalEntry.objects.create(
                warehouse=self.cleaned_data['warehouse'],
                batch=batch,
                entry_type=WarehouseJournalEntry.EntryTypeChoice.INCOMING,
                weight_tons=self.cleaned_data['weight_tons'],
                operator=operator
            )
            
            warehouse = self.cleaned_data['warehouse']
            warehouse.current_balance_tons += self.cleaned_data['weight_tons']
            warehouse.save()

        return journal_entry
    

class GrainOutgoingForm(forms.Form):
    """Форма для операцій списання та бронювання існуючих партій."""

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        label="Склад",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    batch = forms.ModelChoiceField(
        queryset=GrainBatch.objects.all(),
        label="Партія зерна для операції",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    entry_type = forms.ChoiceField(
        choices=[
            (WarehouseJournalEntry.EntryTypeChoice.OUTGOING, 
             "Списання/відвантаження"),
            (WarehouseJournalEntry.EntryTypeChoice.RESERVED, 
             "Бронювання під логістику")
        ],
        label="Тип операції",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    weight_tons = forms.FloatField(
        label="Вага (тонн)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'step': '0.01', 
            'min': '0.01'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        warehouse = cleaned_data.get('warehouse')
        weight_tons = cleaned_data.get('weight_tons')

        if warehouse and weight_tons:
            if warehouse.current_balance_tons < weight_tons:
                raise ValidationError(
                    f"Недостатньо зерна на складі."
                    f"Доступно: {warehouse.current_balance_tons} т, "
                    f"запитувано: {weight_tons} т."
                )

        return cleaned_data

    def save(self, operator):
        with transaction.atomic():
            warehouse = self.cleaned_data['warehouse']
            weight_tons = self.cleaned_data['weight_tons']
            entry_type = self.cleaned_data['entry_type']

            journal_entry = WarehouseJournalEntry.objects.create(
                warehouse=warehouse,
                batch=self.cleaned_data['batch'],
                entry_type=entry_type,
                weight_tons=weight_tons,
                operator_id=operator.id
            )

            if entry_type == WarehouseJournalEntry.EntryTypeChoice.OUTGOING:
                warehouse_db = Warehouse.objects.select_for_update().get(id=warehouse.id)
                warehouse_db.current_balance_tons -= weight_tons
                warehouse_db.save()

        return journal_entry