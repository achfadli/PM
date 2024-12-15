

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='root')  # Ganti dengan username Anda
print(user.is_staff, user.is_superuser)