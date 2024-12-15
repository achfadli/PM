from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .forms import (
    CustomUserCreationForm,
    CustomUserLoginForm,
    UserProfileForm
)
from .models import UserProfile, CustomUser


def register(request):
    """
    View untuk registrasi pengguna baru
    """
    if request.user.is_authenticated:
        messages.info(request, _('You are already logged in.'))
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Simpan user
                user = form.save()

                # Buat profile otomatis
                UserProfile.objects.create(user=user)

                # Login langsung setelah registrasi
                login(request, user)

                # Pesan sukses
                messages.success(
                    request,
                    _('Welcome! Your account has been created successfully.')
                )

                # Redirect ke halaman lengkapi profil
                return redirect('edit_profile')

            except ValidationError as e:
                # Tangani error validasi
                messages.error(request, str(e))
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'title': _('Register')
    })


def user_login(request):
    """
    View untuk login pengguna
    """
    if request.user.is_authenticated:
        messages.info(request, _('You are already logged in.'))
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Autentikasi pengguna
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)

                # Pesan selamat datang
                messages.success(
                    request,
                    _('Welcome back, {}!').format(user.first_name or user.username)
                )

                # Cek kelengkapan profil
                try:
                    profile = user.profile
                    if not profile_is_complete(profile):
                        messages.warning(
                            request,
                            _('Please complete your profile.')
                        )
                        return redirect('edit_profile')
                except UserProfile.DoesNotExist:
                    # Buat profile jika belum ada
                    UserProfile.objects.create(user=user)
                    return redirect('edit_profile')

                return redirect('home')
            else:
                messages.error(request, _('Invalid email or password.'))
    else:
        form = CustomUserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'title': _('Login')
    })


@login_required
def edit_profile(request):
    """
    View untuk mengedit profil pengguna
    """
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=user_profile
        )
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            messages.success(
                request,
                _('Your profile has been updated successfully.')
            )
            return redirect('profile_detail')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'title': _('Edit Profile')
    })


@login_required
def profile_detail(request):
    """
    View untuk menampilkan detail profil
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Buat profile jika belum ada
        profile = UserProfile.objects.create(user=request.user)

    return render(request, 'accounts/profile_detail.html', {
        'user': request.user,
        'profile': profile,
        'title': _('Profile Details')
    })


def logout_view(request):
    """
    View untuk logout
    """
    # Simpan username untuk pesan
    username = request.user.username if request.user.is_authenticated else ''

    # Logout
    logout(request)

    # Pesan sukses logout
    messages.success(
        request,
        _('Goodbye, {}! You have been logged out successfully.').format(username)
    )

    return redirect('login')


def profile_is_complete(profile):
    """
    Fungsi untuk memeriksa kelengkapan profil
    """
    required_fields = [
        'birth_date',
        'phone_number',
        'education_level',
        'occupation'
    ]

    return all(getattr(profile, field) for field in required_fields)


class HomeView(TemplateView):
    """
    View untuk halaman beranda
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['user_profile'] = self.request.user.profile

        return context