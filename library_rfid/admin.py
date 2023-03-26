from django.contrib.admin.models import LogEntry
from pages.models import AdminUser

LogEntry._meta.get_field('user').remote_field.model = AdminUser
