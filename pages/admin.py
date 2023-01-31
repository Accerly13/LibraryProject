from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Admin

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['admin_username', 'admin_password']

admin.site.register(Admin, UserAdmin)