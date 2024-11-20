# core/urls.py
from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView

app_name = 'core'

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('classes/', views.classes, name='classes'),
    path('smn/', views.smn, name='smn'),
    path('logout/', LogoutView.as_view(next_page='core:login', template_name='core/login.html'), name='logout'),
]
