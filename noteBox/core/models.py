from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    

class Class(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    description  = models.TextField(max_length=200)
    teachers = models.ManyToManyField(CustomUser, related_name='teaching_classes', limit_choices_to={'is_teacher':True, 'is_staff':False})
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class ClassEnrollment(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)
    students = models.ManyToManyField(CustomUser, related_name='students_enrolled', limit_choices_to={"is_teacher":False, 'is_staff':False})
    is_active = models.BooleanField(default=True)


