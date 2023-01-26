from django.contrib import admin
from .models import Admins

# Register your models here.

class AdminsAdmin(admin.ModelAdmin):
    list_display = ['admin_username', 'admin_password']

admin.site.register(Admins, AdminsAdmin)