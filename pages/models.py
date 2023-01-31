from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime
from django.utils import timezone

# Create your models here.

now = timezone.now()

class Admin(models.Model):
    admin_id = models.PositiveIntegerField(primary_key=True)
    admin_username = models.CharField(max_length=50, verbose_name='User Name')
    admin_password = models.CharField(max_length=50, verbose_name='Password')

    class Meta:
        db_table = "admin"