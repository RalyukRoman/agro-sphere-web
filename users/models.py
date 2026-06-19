from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Company(models.Model):
    """Модель для представлення компанії."""

    id = models.UUIDField(
        verbose_name="ID",
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
        
    name = models.CharField(
        verbose_name="Назва", 
        max_length=100
    )

    created_at = models.DateTimeField(
        verbose_name="Дата створення", 
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    

class User(AbstractUser):
    """Модель для представлення користувача."""

    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Адміністратор'
        USER = 'user', 'Користувач'

    role = models.CharField(
        verbose_name="Роль в системі",
        max_length=10,
        choices=Roles.choices,
        default=Roles.USER
    )
    
    phone_number = models.CharField(
        verbose_name="Номер телефону",
        max_length=15, 
        blank=True, 
        null=True
    )

    email = models.EmailField(
        verbose_name="Електронна пошта", 
        max_length=100, 
        blank=True, 
        null=True
    )
    
    company = models.ForeignKey(
        verbose_name="Компанія",
        related_name="employees",
        to=Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
