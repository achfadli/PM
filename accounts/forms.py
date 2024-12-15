from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import DateInput
from .models import CustomUser, UserProfile
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator


class CustomDateInput(DateInput):
    input_type = 'date'

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}

        # Default attributes untuk input tanggal
        default_attrs = {
            'class': 'form-control',
            'min': '1900-01-01',  # Batasan tahun minimum
            'max': timezone.now().date().isoformat(),  # Batasan tanggal maksimum (hari ini)
        }

        # Update default attributes dengan attrs yang diberikan
        default_attrs.update(attrs)

        super().__init__(attrs=default_attrs)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email')
        })
    )
    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Choose a username')
        })
    )
    first_name = forms.CharField(
        label=_('First Name'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your first name')
        })
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your last name')
        })
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Create a password')
        })
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm your password')
        })
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')


class CustomUserLoginForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email')
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your password')
        })
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError(_("Invalid email or password."))
        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        label=_('Birth Date'),
        widget=CustomDateInput(),
        required=False
    )

    profile_image = forms.ImageField(
        label=_('Profile Image'),
        widget=forms.FileInput(attrs={
            'class': 'form-control-file'
        }),
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message=_('Only image files are allowed.')
            )
        ],
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'birth_date', 'phone_number', 'education_level',
            'occupation', 'marital_status', 'profile_image',
            'address', 'city', 'country', 'postal_code',
            'bio', 'twitter_username', 'linkedin_username', 'github_username'
        ]

        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter phone number')
            }),
            'education_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter occupation')
            }),
            'marital_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Enter your address')
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter city')
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter country')
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter postal code')
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Tell us about yourself')
            }),
            'twitter_username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Twitter username')
            }),
            'linkedin_username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('LinkedIn username')
            }),
            'github_username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('GitHub username')
            }),
        }

    def clean_profile_image(self):
        """
        Validasi tambahan untuk gambar profil
        """
        image = self.cleaned_data.get('profile_image')

        if image:
            # Batasi ukuran file
            if image.size > 5 * 2048 * 2048:
                raise forms.ValidationError(_('Image file too large ( > 5mb )'))



        return image