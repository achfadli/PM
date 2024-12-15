from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    register,
    user_login,
    edit_profile,
    profile_detail,
    logout_view, HomeView
)





urlpatterns = [

    path('', HomeView.as_view(), name='home'),
    # Registrasi
    path('register/', register, name='register'),

    # Login
    path('login/', user_login, name='login'),

    # Logout
    path('logout/', logout_view, name='logout'),

    # Edit Profil
   # path('edit-profile/', edit_profile, name='edit_profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),

    # Detail Profil
    path('profile/', profile_detail, name='profile_detail'),

    # Password Reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             success_url='/accounts/password-reset/done/'
         ),
         name='password_reset'
         ),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'
         ),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/'
         ),
         name='password_reset_confirm'
         ),

    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'
         ),

    # Ganti Password
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change.html',
             success_url='/accounts/password-change/done/'
         ),
         name='password_change'
         ),

    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ),
         name='password_change_done'
         ),
]

