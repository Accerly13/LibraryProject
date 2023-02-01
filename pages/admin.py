from django.contrib import admin
from .models import UserInfo, AdminUser, Department, College

admin.site.register(AdminUser)
admin.site.register(UserInfo)
admin.site.register(Department)
admin.site.register(College)