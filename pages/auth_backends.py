from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import AdminUser

class AdminUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            admin_user = AdminUser.objects.get(username=username)
            print(admin_user.is_active)
            if admin_user.password == password:
                # Create an instance of AdminUser to authenticate and log in
                user = admin_user
                return user
        except AdminUser.DoesNotExist:
            return None