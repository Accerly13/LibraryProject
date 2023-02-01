from django.contrib import admin
from .models import UserInfo, AdminUser

admin.site.register(AdminUser)
admin.site.register(UserInfo)