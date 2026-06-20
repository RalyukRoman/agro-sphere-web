from django.db.models.signals import post_migrate
from django.db.models import Q
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name != 'users':
        return
    
    # ==========================================
    #  ГРУПА "АДМІНІСТРАТОРИ"
    # ==========================================

    admin_group, created = Group.objects.get_or_create(name='Admins')

    all_apps_permissions = Permission.objects.filter(
        Q(content_type__app_label='geo_analytics') |
        Q(content_type__app_label='smart_planning') |
        Q(content_type__app_label='warehousing') |
        Q(content_type__app_label='users')
    )

    if all_apps_permissions.exists():
        admin_group.permissions.set(all_apps_permissions)
        print(f"Групі 'Адміністратори' успішно призначено {all_apps_permissions.count()} прав.")

    # ==========================================
    #  ГРУПА "КОРИСТУВАЧІ"
    # ==========================================

    users_group, created = Group.objects.get_or_create(name='Users')

    user_permissions = all_apps_permissions.exclude(
        codename__in=[
            'add_field', 'change_field', 'delete_field',
            'add_user', 'change_user', 'delete_user',
            'add_company', 'change_company', 'delete_company',
            'add_warehouse', 'change_warehouse', 'delete_warehouse',
            'add_cropculture', 'change_cropculture', 'delete_cropculture'
        ]
    )

    if user_permissions.exists():
        users_group.permissions.set(user_permissions)
        print(f"Групі 'Users' успішно призначено {user_permissions.count()} прав.")