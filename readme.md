Email address: ach@gmail.com
Username: root  
Password: achfadli0858
Password (again): 
Superuser created successfully.


### kode untuk membuat super user 

```python
# python manage.py shell <-- ketik perintah ini di terminal

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='your_username')  # Ganti dengan username Anda
print(user.is_staff, user.is_superuser)


```

## account super admin 2
Email address: root@gmail.com
Username: root1
Password: achfadli0858
Password (again): 
Superuser created successfully.


# Contoh pengembangan View 
```python
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm  # Pastikan Anda memiliki form yang sesuai

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile_detail')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    # Implementasi login
    pass

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def edit_profile(request):
    # Implementasi edit profil
    pass

@login_required
def profile_detail(request):
    # Implementasi detail profil
    pass

def password_change(request):
    # Implementasi ganti password
    pass

def password_reset(request):
    # Implementasi reset password
    pass