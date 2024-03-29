from django.db import models

# Create your models here.
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Create your models here.

now = timezone.now()


class MyUserManager(BaseUserManager):
    def create_user(self, admin_id, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        user = self.model(admin_id=admin_id, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, admin_id, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(admin_id, username, password=password, **extra_fields)
    

class AdminUser(AbstractBaseUser, PermissionsMixin):
    admin_id = models.PositiveIntegerField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'admin'
    
    
class College(models.Model):
    college_id = models.AutoField(primary_key=True, unique=True)
    college_name = models.CharField(max_length=150, verbose_name='college_name')

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
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if not self.course_id:
            # get the highest existing ID and add 1
            last_id = Course.objects.order_by('-course_id').first()
            self.course_id = 1 if last_id is None else last_id.course_id + 1
        super().save(*args, **kwargs)

    class Meta:
        db_table = "course"

class UserInfo(models.Model):
    user_idno = models.CharField(primary_key=True, max_length=20, unique=True)
    alternative_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50, verbose_name='f_name')
    middle_name = models.CharField(max_length=50, verbose_name='m_name')
    last_name = models.CharField(max_length=50, verbose_name='l_name')
    gender = models.CharField(max_length=1, verbose_name='gender')
    comment = models.CharField(max_length=50, verbose_name='comment')
    type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    class Meta:
        db_table = "users"

class DatesLogin(models.Model):
    dates = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(null=True, blank=True)
    user = models.CharField(max_length=50)

    class Meta:
        db_table = "dates_login"

class Transactions(models.Model):
    dates = models.DateField()
    title = models.CharField(max_length=300, verbose_name='title')
    transact = models.CharField(max_length=10, verbose_name='transact', default='')

    class Meta:
        db_table = "transactions"

class Visitors(models.Model):
    school = models.CharField(max_length=300, verbose_name='school')
    purpose = models.CharField(max_length=300, verbose_name='purpose')
    name = models.CharField(max_length=300, verbose_name='name')
    email = models.CharField(max_length=50, verbose_name='email')
    phone = models.CharField(max_length=20, verbose_name='phone')
    student_id = models.CharField(max_length=20, verbose_name='student_id')
    dates = models.DateField()
    time = models.TimeField()

    class Meta:
        db_table = "visitors"



