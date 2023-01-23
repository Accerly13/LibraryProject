from django.db import models
from datetime import datetime
from django.utils import timezone

# Create your models here.

now = timezone.now()

class Admins(models.Model):
    admins = models.CharField(max_length=50, verbose_name='User Name')

   
