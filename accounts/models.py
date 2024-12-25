import os
import uuid
from cProfile import Profile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission, User
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator, EmailValidator, RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from .managers import CustomUserManager  # Import CustomUser Manager
from enum import Enum
from django.core.files.base import ContentFile
from PIL import Image as PilImage
import io

def user_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_images', str(instance.user.id), filename)


class CustomUser (AbstractBaseUser , PermissionsMixin):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('id', 'Bahasa Indonesia'),
    ]

    THEME_CHOICES = [
        ('default', 'Default'),
        ('modern', 'Modern'),
        ('gradient', 'Gradient'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, validators=[EmailValidator()])
    username = models.CharField(_('username'), max_length=50, unique=True, validators=[
        RegexValidator(r'^[\w.@+-]+$', _('Enter a valid username. Use letters, numbers, and @/./+/-/_ only.'))
    ])
    first_name = models.CharField(_('First Name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_verified = models.BooleanField(_('verified'), default=False)
    two_factor_enabled = models.BooleanField(_('two-factor authentication'), default=False)
    login_count = models.PositiveIntegerField(_('login count'), default=0)
    last_login_ip = models.GenericIPAddressField(_('last login IP'), null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_activity = models.DateTimeField(_('last activity'), null=True, blank=True)
    language_preference = models.CharField(_('language preference'), max_length=10, choices=LANGUAGE_CHOICES, default='en')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='default')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [models.Index(fields=['email', 'username'])]

    def __str__(self):
        return self.email

    def get_all_users(self):
        """
        Metode untuk mendapatkan semua user
        """
        return get_user_model().objects.all()


    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def get_short_name(self):
        return self.first_name or self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def natural_key(self):
        return (self.username,)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Ubah nama ini sesuai kebutuhan
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Ubah nama ini sesuai kebutuhan
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say')
    ], blank=True, default='N')

    EDUCATION_LEVELS = [
        ('SD', _('Elementary School')),
        ('SMP', _('Junior High School')),
        ('SMA', _('Senior High School')),
        ('D3', _('Diploma')),
        ('S1', _('Bachelor')),
        ('S2', _('Master')),
        ('S3', _('Doctorate')),
        ('OTHER', _('Other'))
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', _('Single')),
        ('M', _('Married')),
        ('D', _('Divorced')),
        ('W', _('Widowed'))
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(_('Birth Date'), null=True, blank=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )

    phone_number = models.CharField(  # Perbaikan di sini
        _('Phone Number'),
        validators=[phone_regex],
        max_length=15,
        blank=True,
        null=True
    )

    education_level = models.CharField(_('Education Level'), max_length=10, choices=EDUCATION_LEVELS, blank=True)
    occupation = models.CharField(_('Occupation'), max_length=100, blank=True)
    marital_status = models.CharField(_('Marital Status'), max_length=1, choices=MARITAL_STATUS_CHOICES, blank=True)

    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )

    def save(self, *args, **kwargs):
        if self.profile_image:
            img = PilImage.open(self.profile_image)
            img = img.convert('RGB')
            img.thumbnail((300, 300))  # Mengubah ukuran gambar menjadi 300x300
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)  # Menyimpan gambar dengan kualitas 85
            img_file = ContentFile(img_io.getvalue(), name=self.profile_image.name)
            self.profile_image = img_file
        super().save(*args, **kwargs)

    address = models.TextField(_('Address'), blank=True, null=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)

    bio = models.TextField(_('Bio'), blank=True, null=True)
    twitter_username = models.CharField(_('Twitter Username'), max_length=100, blank=True)
    linkedin_username = models.CharField(_('LinkedIn Username'), max_length=100, blank=True)
    github_username = models.CharField(_('GitHub Username'), max_length=100, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('User  Profile')
        verbose_name_plural = _('User  Profiles')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_complete(self):
        required_fields = ['birth_date', 'phone_number', 'education_level', 'occupation']
        return all(getattr(self, field) for field in required_fields)

    def get_completion_percentage(self):
        total_fields = ['birth_date', 'phone_number', 'education_level', 'occupation', 'profile_image']
        completed_fields = sum(1 for field in total_fields if getattr(self, field))
        return int((completed_fields / len(total_fields)) * 100)

    def get_incomplete_fields(self):
        required_fields = ['birth_date', 'phone_number', 'education_level', 'occupation']
        return [field for field in required_fields if not getattr(self, field)]


class UserActivity(models.Model):
    class ActivityType(Enum):
        LOGIN = 'LOGIN'
        LOGOUT = 'LOGOUT'
        REGISTRATION = 'REGISTRATION'
        PROFILE_UPDATE = 'PROFILE_UPDATE'
        PASSWORD_CHANGE = 'PASSWORD_CHANGE'
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION'
        ACCOUNT_ACTIVATION = 'ACCOUNT_ACTIVATION'
        TWO_FACTOR_AUTH = 'TWO_FACTOR_AUTH'
        PASSWORD_RESET = 'PASSWORD_RESET'
        DEVICE_LOGIN = 'DEVICE_LOGIN'
        UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS'

    class SeverityLevel(Enum):
        INFO = 'INFO'
        WARNING = 'WARNING'
        CRITICAL = 'CRITICAL'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities', verbose_name=_('User '))
    activity_type = models.CharField(_('Activity Type'), max_length=30, choices=[(tag.value, tag.name) for tag in ActivityType])
    severity = models.CharField(_('Severity Level'), max_length=20, choices=[(tag.value, tag.name) for tag in SeverityLevel], default=SeverityLevel.INFO.value)
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User  Agent'), blank=True, null=True)
    location = models.JSONField(_('Location Information'), null=True, blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True, db_index=True)
    additional_info = models.JSONField(_('Additional Information'), null=True, blank=True)
    is_suspicious = models.BooleanField(_('Suspicious Activity'), default=False)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

    @classmethod
    def log_activity(cls, user, activity_type, ip_address=None, user_agent=None, location=None, additional_info=None, severity=SeverityLevel.INFO.value, is_suspicious=False):
        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            additional_info=additional_info or {},
            severity=severity,
            is_suspicious=is_suspicious
        )

    @classmethod
    def get_user_activities(cls, user, activity_type=None, days=30):
        from django.utils import timezone

        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        queryset = cls.objects.filter(user=user, timestamp__gte=cutoff_date)

        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        return queryset.order_by('-timestamp')

    class Meta:
        verbose_name = _('User  Activity')
        verbose_name_plural = _('User  Activities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type', 'timestamp']),
            models.Index(fields=['is_suspicious', 'timestamp']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'activity_type', 'timestamp'], name='unique_user_activity')
        ]

# next bakalalah di pindah ke Signal.py

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Otomatis membuat profile saat user dibuat
    """
    if created:
        Profile.objects.create(
            user=instance,
            # Anda bisa menambahkan default values jika diperlukan
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Menyimpan profile saat user diupdate
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

