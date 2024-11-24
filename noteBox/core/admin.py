from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Class, ClassEnrollment, StudyMaterials, Doubt, DoubtResponse, TimeBoxedSession

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

@admin.register(StudyMaterials)
class StudyMaterialsAdmin(admin.ModelAdmin):
    list_display = ('title', 'material_type', 'created_by', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('material_type', 'created_at')

    # Customize how questions are displayed
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['questions'].widget.attrs.update({'rows': 5, 'style': 'width: 70%;'})
        return form

# Unregister the default User model if it was previously registered
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Class)
admin.site.register(ClassEnrollment)
admin.site.register(Doubt)
admin.site.register(DoubtResponse)
admin.site.register(TimeBoxedSession)
