from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import TimeBoxedSession

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class TimeBoxedSessionForm(forms.ModelForm):
    class Meta:
        model = TimeBoxedSession
        fields = ['class_instance', 'title', 'study_material', 'start_time', 
                  'duration_minutes', 'created_by']
        
        # You can customize the form field widgets if needed
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'duration_minutes': forms.NumberInput(attrs={'min': 1}),
        }