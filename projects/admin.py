from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import ProjectCategory, Project, ProjectTask


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {
            'fields': ('name', 'slug')
        }),
        (_('Description'), {
            'fields': ('description',)
        })
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner', 'category', 'status',
        'priority', 'progress', 'start_date',
        'end_date', 'is_overdue'
    )
    list_filter = (
        'status', 'priority', 'category',
        'start_date', 'end_date'
    )
    search_fields = (
        'title', 'description',
        'owner__username', 'category__name'
    )

    # Inline untuk Task
    class ProjectTaskInline(admin.TabularInline):
        model = ProjectTask
        extra = 0
        readonly_fields = ('created_at', 'updated_at')
        fields = (
            'title', 'assigned_to', 'status',
            'priority', 'due_date'
        )

    inlines = [ProjectTaskInline]

    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'title', 'slug', 'description',
                'owner', 'category'
            )
        }),
        (_('Project Details'), {
            'fields': (
                'status', 'priority',
                'start_date', 'end_date',
                'progress', 'budget'
            )
        }),
        (_('Team'), {
            'fields': ('team_members',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}

    def is_overdue(self, obj):
        return obj.is_overdue()

    is_overdue.boolean = True
    is_overdue.short_description = _('Overdue')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'project', 'assigned_to',
        'status', 'priority', 'due_date',
        'is_overdue'
    )
    list_filter = (
        'status', 'priority',
        'project', 'assigned_to',
        'due_date'
    )
    search_fields = (
        'title', 'description',
        'project__title', 'assigned_to__username'
    )

    fieldsets = (
        (_('Task Information'), {
            'fields': (
                'project', 'title', 'description'
            )
        }),
        (_('Task Details'), {
            'fields': (
                'assigned_to', 'status',
                'priority', 'due_date'
            )
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at', 'updated_at')

    def is_overdue(self, obj):
        return obj.is_overdue()

    is_overdue.boolean = True
    is_overdue.short_description = _('Overdue')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(
            Q(project__owner=request.user) |
            Q(assigned_to=request.user)
        )


# Kustomisasi Admin Global
admin.site.site_header = "Project Management System"
admin.site.site_title = "PMS Admin"
admin.site.index_title = "Welcome to Project Management System"