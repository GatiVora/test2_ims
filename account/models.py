from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from .managers import UserManager
# Create your models here.

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractBaseUser,TimeStampModel,PermissionsMixin):

    USER_ROLES = (
        ('admin','Admin'),
        ('interviewer','Interviewer'),
        ('candidate','Candidate'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=15,choices=USER_ROLES,default='candidate')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','role']

    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
    

    objects = UserManager()

    



