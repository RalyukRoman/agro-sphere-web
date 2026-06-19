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
