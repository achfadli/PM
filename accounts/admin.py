from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile, UserActivity

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'last_name',
        'is_staff', 'is_active', 'is_verified',
        'date_joined', 'last_activity'
    )
    list_filter = (
        'is_staff', 'is_active', 'is_verified',
        'language_preference', 'theme',
        'date_joined', 'last_activity'
    )
    search_fields = (
        'email', 'username', 'first_name', 'last_name'
    )
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal Info'), {
            'fields': (
                'first_name', 'last_name',
                'language_preference', 'theme'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_verified',
                'two_factor_enabled',
                'groups', 'user_permissions'
            ),
        }),
        (_('Login & Security'), {
            'fields': (
                'login_count', 'last_login_ip',
                'last_activity', 'last_login'
            )
        }),
        (_('Important Dates'), {
            'fields': ('date_joined',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2',
                'is_staff', 'is_active', 'is_verified'
            ),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'gender', 'education_level',
        'occupation', 'marital_status',
        'get_completion_percentage'
    )
    list_filter = (
        'gender', 'education_level',
        'marital_status', 'city', 'country'
    )
    search_fields = (
        'user__username', 'user__email',
        'phone_number', 'occupation',
        'city', 'country'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('User Information'), {
            'fields': (
                'user', 'gender', 'birth_date',
                'phone_number'
            )
        }),
        (_('Professional Details'), {
            'fields': (
                'education_level', 'occupation',
                'marital_status'
            )
        }),
        (_('Contact Information'), {
            'fields': (
                'address', 'city', 'country',
                'postal_code'
            )
        }),
        (_('Social Links'), {
            'fields': (
                'twitter_username',
                'linkedin_username',
                'github_username'
            )
        }),
        (_('Profile Media'), {
            'fields': (
                'profile_image', 'bio'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_completion_percentage(self, obj):
        return obj.get_completion_percentage()
    get_completion_percentage.short_description = 'Profile Completion'

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'activity_type', 'severity',
        'timestamp', 'is_suspicious',
        'ip_address'
    )
    list_filter = (
        'activity_type', 'severity',
        'is_suspicious', 'timestamp'
    )
    search_fields = (
        'user__username', 'user__email',
        'ip_address', 'activity_type'
    )
    readonly_fields = ('timestamp',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    fieldsets = (
        (_('User & Activity'), {
            'fields': (
                'user', 'activity_type',
                'severity', 'is_suspicious'
            )
        }),
        (_('Technical Details'), {
            'fields': (
                'ip_address', 'user_agent',
                'location', 'additional_info'
            )
        }),
        (_('Timestamp'), {
            'fields': ('timestamp',)
        }),
    )

# Kustomisasi Admin Global
admin.site.site_header = "User Management System"
admin.site.site_title = "UMS Admin"
admin.site.index_title = "Welcome to User Management System"