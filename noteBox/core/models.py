from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta

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

    def __str__(self) -> str:
        return self.class_instance.name

class StudyMaterials(models.Model):
    MATERIAL_TYPES = [
        ('PDF', 'PDF Document'),
        ('VIDEO', 'Video'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    lass_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='study_materials')
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPES)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='study_materials/', null=True, blank=True)  # For PDF/Video uploads
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_teacher':True})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    questions = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,  # Ensure proper encoding
        blank=True,  # Optional field
        help_text="List of question and answer pairs in JSON format"
    )

    def __str__(self) -> str:
        return self.title


class Doubt(models.Model):
    """Model for student doubts/questions"""
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('ANSWERED', 'Answered'),
        ('CLOSED', 'Closed'),
    ]
    
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doubts')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='doubts')
    study_material = models.ForeignKey(StudyMaterials, on_delete=models.CASCADE, related_name='doubts', null=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.content

class DoubtResponse(models.Model):
    """Model for responses to doubts"""
    doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TimeBoxedSession(models.Model):
    """Model for time-boxed study sessions"""
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timeboxed_sessions')
    title = models.CharField(max_length=200)
    study_material = models.ForeignKey(StudyMaterials, on_delete=models.CASCADE, related_name="material_for_session")
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    end_time = models.DateTimeField(editable=False, null=True, blank=True) 
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        
        super().save(*args, **kwargs) 

    def __str__(self):
        return self.title