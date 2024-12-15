from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser , UserProfile, UserActivity

@admin.register(CustomUser )
class CustomUserAdmin(UserAdmin):
    """
    Konfigurasi admin untuk model user kustom
    """
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_verified',
        'date_joined', 'last_activity'
    )
    list_filter = (
        'is_staff', 'is_active', 'is_verified',
        'date_joined', 'last_activity'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'language_preference')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'is_verified', 'two_factor_enabled'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_activity')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Konfigurasi admin untuk profil user
    """
    list_display = (
        'user', 'gender', 'birth_date',
        'education_level', 'occupation',
        'created_at', 'updated_at'
    )
    search_fields = ('user__username', 'user__email', 'occupation', 'city')
    list_filter = ('gender', 'education_level', 'marital_status')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Konfigurasi admin untuk aktivitas user
    """
    list_display = (
        'user', 'activity_type', 'severity',
        'ip_address', 'timestamp', 'is_suspicious'
    )
    list_filter = ('activity_type', 'severity', 'is_suspicious', 'timestamp')
    search_fields = ('user__username', 'user__email', 'ip_address')
    date_hierarchy = 'timestamp'