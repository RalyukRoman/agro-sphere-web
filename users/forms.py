from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group

from .models import Company
import uuid

from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm
)

User = get_user_model()


class CompanyForm(forms.ModelForm):
    """Форма для створення компанії разом з її адміністратором."""
    
    admin_username = forms.CharField(
        label="Ім'я користувача (логін)",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'username'
        })
    )

    admin_email = forms.EmailField(
        label="Електронна пошта",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'example@mail.com'
        })
    )

    admin_password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 
            'Мінімум 6 символів'
        }),
        min_length=6
    )

    admin_phone = forms.CharField(
        label="Номер телефону",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+380...'
        })
    )

    class Meta:
        model = Company
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введіть назву компанії'
            }),
        }

    def clean_admin_username(self):
        username = self.cleaned_data.get('admin_username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Користувач з таким логіном вже існує в системі."
            )
        return username

    def save(self, commit=True):
        with transaction.atomic():
            company = super().save(commit=commit)
            
            username = self.cleaned_data.get('admin_username')
            email = self.cleaned_data.get('admin_email')
            password = self.cleaned_data.get('admin_password')
            phone = self.cleaned_data.get('admin_phone')

            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone,
                company=company,
                role='admin'
            )
            
            group, created = Group.objects.get_or_create(name='Admins')
            admin_user.groups.add(group)
            
        return company


class UserRegistrationForm(UserCreationForm):
    """Форма для реєстрації користувача за ручним введенням ID компанії."""

    company_id = forms.CharField(
        label="Ідентифікатор компанії (UUID)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Наприклад: 8f3b9c72-411a-4d92-bb52-ef110839212d'
        }),
        help_text="Отримайте цей код у адміністратора вашої компанії.",
        required=True
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number')
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Введіть логін'
            }),
            
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'example@mail.com'
            }),

            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+380...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_company_id(self):
        """Валідація введеного ID компанії."""
        company_id_raw = self.cleaned_data.get('company_id').strip()
        
        try:
            uuid.UUID(company_id_raw)
        except ValueError:
            raise ValidationError(
                "Некоректний формат ідентифікатора компанії."
            )
            
        try:
            company = Company.objects.get(id=company_id_raw)
        except Company.DoesNotExist:
            raise ValidationError(
                "Компанію з таким ідентифікатором не знайдено."
            )
            
        return company

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)
            user.company = self.cleaned_data.get('company_id')
            user.role = User.Roles.USER
            
            if commit:
                user.save()
                group, created = Group.objects.get_or_create(name='Users')
                user.groups.add(group)
                
        return user


class UserLoginForm(AuthenticationForm):
    """Форма для входу на сайт."""

    username = forms.CharField(
        label="Логін",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ваш логін'
        })
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ваш пароль'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Форма для редагування профілю."""
    
    class Meta:
        model = User
        fields = ['email', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'phone_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }