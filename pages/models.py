from django.db import models

# Create your models here.
from datetime import datetime
from django.utils import timezone

# Create your models here.

now = timezone.now()

class UserInfo(models.Model):
    idnum = models.CharField(primary_key=True, max_length=50, unique=True)
    fname = models.CharField(max_length=50, verbose_name='f_name')
    mname = models.CharField(max_length=50, verbose_name='m_name')
    lname = models.CharField(max_length=50, verbose_name='l_name')
    gender = models.CharField(max_length=1, verbose_name='gender')
    course = models.CharField(max_length=50, verbose_name='course')
    comment = models.CharField(max_length=50, verbose_name='comment')
    usertype = models.CharField(max_length=50, verbose_name='usertype')
    dept = models.CharField(max_length=50, verbose_name='dept')

    class Meta:
        db_table = "users"

class AdminUser(models.Model):
    admin_id = models.PositiveIntegerField(primary_key=True)
    admin_username = models.CharField(max_length=50, verbose_name='User Name')
    admin_password = models.CharField(max_length=50, verbose_name='Password')

    class Meta:
        db_table = "adminuser"

class Department(models.Model):
    department_id = models.IntegerField(primary_key=True, unique=True)
    dept_name = models.CharField(max_length=50, verbose_name='department_name')

    class Meta:
        db_table = "department"

class College(models.Model):
    college_id = models.IntegerField(primary_key=True, unique=True)
    college_name = models.CharField(max_length=50, verbose_name='college_name')
    class Meta:
        db_table = "college"




