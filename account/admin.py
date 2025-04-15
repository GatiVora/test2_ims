from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ()

admin.site.register(User,CustomUserAdmin)