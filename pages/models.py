from django.db import models

# Create your models here.
from datetime import datetime
from django.utils import timezone

# Create your models here.

now = timezone.now()

class AdminUser(models.Model):
    admin_id = models.PositiveIntegerField(primary_key=True)
    admin_username = models.CharField(max_length=50, verbose_name='User Name')
    admin_password = models.CharField(max_length=50, verbose_name='Password')

    class Meta:
        db_table = "admin"

class College(models.Model):
    college_id = models.AutoField(primary_key=True, unique=True)
    college_name = models.CharField(max_length=50, verbose_name='college_name')

    class Meta:
        db_table = "college"


class Department(models.Model):
    department_id = models.AutoField(primary_key=True, unique=True)
    department_name = models.CharField(max_length=50, verbose_name='department_name')
    college = models.ForeignKey(College, on_delete=models.CASCADE, default='')

    class Meta:
        db_table = "departments"

class UserType(models.Model):
    type_id = models.IntegerField(primary_key=True, unique=True)
    type_name = models.CharField(max_length=50, verbose_name='usertype_name')

    class Meta:
        db_table = "usertype"

class Course(models.Model):
    course_id = models.IntegerField(primary_key=True, unique=True)
    course_name = models.CharField(max_length=50, verbose_name='course_name')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default='')

    class Meta:
        db_table = "course"

class UserInfo(models.Model):
    user_idno = models.CharField(primary_key=True, max_length=15, unique=True, default='')
    first_name = models.CharField(max_length=50, verbose_name='f_name')
    middle_name = models.CharField(max_length=50, verbose_name='m_name')
    last_name = models.CharField(max_length=50, verbose_name='l_name')
    gender = models.CharField(max_length=1, verbose_name='gender')
    comment = models.CharField(max_length=50, verbose_name='comment')
    type = models.ForeignKey(UserType, on_delete=models.CASCADE, default='')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default='')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default='', related_name='users')

    class Meta:
        db_table = "users"

class DatesLogin(models.Model):
    dates = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, default='')

    class Meta:
        db_table = "dates_login"

