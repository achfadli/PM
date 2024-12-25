from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse


class ProjectCategory(models.Model):
    CATEGORY_CHOICES = [
        ('web', _('Web Development')),
        ('mobile', _('Mobile Development')),
        ('data', _('Data Science')),
        ('design', _('UI/UX Design')),
        ('ai', _('Artificial Intelligence')),
        ('other', _('Other'))
    ]

    name = models.CharField(
        verbose_name=_('Category Name'),
        max_length=50,
        unique=True,
        choices=CATEGORY_CHOICES
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        blank=True
    )

    def save(self, *args, **kwargs):
        # Automatically generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_category_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = _('Project Category')
        verbose_name_plural = _('Project Categories')
        ordering = ['name']


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('on_hold', _('On Hold')),
        ('cancelled', _('Cancelled'))
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent'))
    ]

    title = models.CharField(
        verbose_name=_('Project Title'),
        max_length=200,
        validators=[MinLengthValidator(5)]
    )
    slug = models.SlugField(
        unique=True,
        max_length=250,
        blank=True
    )
    description = models.TextField(
        verbose_name=_('Project Description'),
        blank=True,
        null=True
    )

    # Relasi dengan User
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )

    # Relasi Many-to-Many untuk tim proyek
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='team_projects',
        blank=True
    )

    # Kategori Proyek
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='projects'
    )

    # Status dan Prioritas
    status = models.CharField(
        verbose_name=_('Project Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    priority = models.CharField(
        verbose_name=_('Project Priority'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='low'
    )

    # Tanggal dan Waktu
    start_date = models.DateField(
        verbose_name=_('Start Date'),
        null=True,
        blank=True
    )
    end_date = models.DateField(
        verbose_name=_('End Date'),
        null=True,
        blank=True
    )

    # Progress
    progress = models.IntegerField(
        verbose_name=_('Project Progress'),
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )

    # Biaya dan Sumber Daya
    budget = models.DecimalField(
        verbose_name=_('Project Budget'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)

        # Validate dates
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError(_("End date must be after start date"))

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    def is_overdue(self):
        """
        Cek apakah proyek sudah melewati tanggal selesai
        """
        return self.end_date and self.end_date < timezone.now().date()

    def get_duration(self):
        """
        Hitung durasi proyek
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return None

    def update_progress(self):
        """
        Update progress proyek berdasarkan task
        """
        tasks = self.tasks.all()
        if tasks:
            completed_tasks = tasks.filter(status='done').count()
            total_tasks = tasks.count()
            self.progress = (completed_tasks / total_tasks) * 100
            self.save()

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
        unique_together = ['title', 'owner']


class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('todo', _('To Do')),
        ('in_progress', _('In Progress')),
        ('review', _('In Review')),
        ('done', _('Done'))
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent'))
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(
        verbose_name=_('Task Title'),
        max_length=200
    )
    description = models.TextField(
        verbose_name=_('Task Description'),
        blank=True,
        null=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks'
    )
    status = models.CharField(
        verbose_name=_('Task Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )
    priority = models.CharField(
        verbose_name=_('Task Priority'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    due_date = models.DateField(
        verbose_name=_('Due Date'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Validate due date
        if self.due_date and self.due_date < timezone.now().date():
            raise ValueError(_("Due date cannot be in the past"))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def is_overdue(self):
        """
        Cek apakah tugas sudah melewati tanggal jatuh tempo
        """
        return self.due_date and self.due_date < timezone.now().date()

    class Meta:
        verbose_name = _('Project Task')
        verbose_name_plural = _('Project Tasks')
        ordering = ['due_date']
        unique_together = ['title', 'project']  # Ensure task titles are unique within a project