from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Class, ClassEnrollment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_teacher', 'is_staff', 'is_active')
    list_filter = ('is_teacher', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_teacher')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name' , 'password1', 'password2', 'is_teacher', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Unregister the default User model if it was previously registered
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Class)
admin.site.register(ClassEnrollment)