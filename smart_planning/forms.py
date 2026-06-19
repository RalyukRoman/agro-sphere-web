from django import forms
from .models import CropCulture
from geo_analytics.models import Field


class CropCultureForm(forms.ModelForm):
    """Форма для налаштування параметрів сільськогосподарської культури."""

    class Meta:
        model = CropCulture
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'base_market_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SmartPlanningCalculateForm(forms.Form):
    """Спеціальна форма для розрахунку оптимального плану посіву."""

    field = forms.ModelChoiceField(
        queryset=Field.objects.all(),
        label="Оберіть поле",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    budget = forms.FloatField(
        label="Доступний бюджет",
        min_value=0.0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Залиште порожнім, якщо немає обмежень'
        })
    )

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget < 0:
            raise forms.ValidationError("Бюджет не може бути від'ємним.")
        return budget