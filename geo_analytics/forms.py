from django import forms
from django.contrib.gis import forms as gis_forms
from django.contrib.auth import get_user_model
from .models import Field

User = get_user_model()


class FieldForm(gis_forms.ModelForm):
    """Форма для створення поля з використанням карти для малювання меж."""

    class Meta:
        model = Field
        fields = ['name', 'crop_status', 'geom', 'area_hectares']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'crop_status': forms.Select(attrs={'class': 'form-select'}),
            
            'geom': gis_forms.OSMWidget(attrs={
                'map_width': '100%',
                'map_height': 550,
            }),

            'area_hectares': forms.HiddenInput(), 
        }


class FieldMetricHistoryForm(forms.ModelForm):
    """Форма для запису метрик стану поля."""

    class Meta:
        model = FieldMetricHistory
        fields = '__all__'
        widgets = {
            'field': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ndvi_index': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'soil_moisture': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'weather_raw_data': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }