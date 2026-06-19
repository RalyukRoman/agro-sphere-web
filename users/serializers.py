from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, Company


class CompanyCreateWithAdminSerializer(serializers.ModelSerializer):
    """Серіалізатор для створення компанії разом з її адміністратором."""
    
    admin_username = serializers.CharField(
        write_only=True
    )

    admin_email = serializers.EmailField(
        write_only=True,
        required=False, 
    )

    admin_password = serializers.CharField(
        write_only=True, 
        min_length=6
    )

    admin_phone = serializers.CharField(
        write_only=True, 
        required=False, 
        allow_blank=True
    )

    class Meta:
        model = Company
        fields = [
            'id', 'name',
            'admin_username', 'admin_email', 
            'admin_password', 'admin_phone'
        ]

    def validate_admin_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Користувач з таким ім'ям вже існує."
            )
        return value

    def create(self, validated_data):
        admin_username = validated_data.pop('admin_username')
        admin_email = validated_data.pop('admin_email', None)
        admin_password = validated_data.pop('admin_password')
        admin_phone = validated_data.pop('admin_phone', None)

        with transaction.atomic():
            company = Company.objects.create(**validated_data)

            User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                phone_number=admin_phone,
                company=company,
                role=User.Roles.ADMIN,
            )

        return company
    

class RegisterSerializer(serializers.ModelSerializer):
    """Серіалізатор для створення нового користувача."""

    password = serializers.CharField(
        write_only=True, 
        min_length=6
    )

    company_id = serializers.UUIDField(
        required=False, 
        write_only=True, 
        allow_null=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 
            'phone_number', 'company_id'
        ]

    def validate_company_id(self, value):
        if value and not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Вказаної компанії не існує."
            )
        return value

    def create(self, validated_data):
        company_id = validated_data.pop('company_id', None)
        user = User.objects.create_user(**validated_data)

        if company_id:
            user.company_id = company_id
            user.save()
            
        return user


class LoginSerializer(serializers.Serializer):
    """Серіалізатор для входу користувача."""

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):
        user = authenticate(
            username=data.get('username'), 
            password=data.get('password')
        )

        if not user:
            raise serializers.ValidationError(
                "Невірне ім'я користувача або пароль."
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "Цей акаунт деактивовано."
            )
        
        data['user'] = user
        return data