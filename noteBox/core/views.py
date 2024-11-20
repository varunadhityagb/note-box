# core/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import CustomUser, Class, ClassEnrollment, StudyMaterials, PDFAnnotation, Doubt, DoubtResponse, TimeBoxedSession
from .forms import TimeBoxedSessionForm
from django.utils import timezone


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'core/login.html'
    success_url = reverse_lazy('core:classes')

    def get_success_url(self):
        return reverse_lazy('core:classes')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)
    

class CustomLogoutView(LogoutView):
    next_page = 'core:login'
    http_method_names = ['get', 'post'] 

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        logout(request)  
        request.session.flush()  
        request.session.clear_expired()  
        return response
    


@login_required(login_url="/")
def classes(request):
    if not request.user.is_authenticated:
        return redirect('core:login')
    elif request.user.is_staff:
        return redirect('/admin')
    
   

    if not request.user.is_teacher:
        student = CustomUser.objects.get(username=request.user.username)
        class_enrollments = ClassEnrollment.objects.filter(students=student)
        class_list = []
        for enrollment in class_enrollments:
            class_instance = enrollment.class_instance
            class_list.append(class_instance)
    else:
        class_list = Class.objects.filter(teachers=request.user)
    return render(request, 'core/classes.html', {'user': request.user, 'classes':class_list})

@login_required(login_url="/")
def class_redirect(request,class_name):
    if not request.user.is_authenticated:
        return redirect('core:login')
    elif request.user.is_staff:
        return redirect('/admin')
    
    if request.method == 'POST':
        form = TimeBoxedSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("success")
    else:
        form = TimeBoxedSessionForm()

    class_instance = Class.objects.get(name=class_name)
    materials = StudyMaterials.objects.filter(lass_instance=class_instance)
    timeboxed_sessions = TimeBoxedSession.objects.filter(class_instance = class_instance, start_time__lte=timezone.now())
    sessions_list = []
    for session in timeboxed_sessions:
        sessions_list.append(session)

    return render(request, 'core/class.html', {'user': request.user, 'materials':materials, 'form':form, 'timeboxes':sessions_list})


@login_required(login_url="/")
def pdf_view(request, class_name, fileName):
    if not request.user.is_authenticated:
        return redirect('core:login')
    elif request.user.is_staff:
        return redirect('/admin')
    
    pdfs = StudyMaterials.objects.all()
    class_instance = Class.objects.get(name=class_name)

    pdf_material = StudyMaterials.objects.filter(
        lass_instance=class_instance, 
        material_type='PDF', 
        title=fileName
    ).first() 

    document = get_object_or_404(StudyMaterials, id=pdf_material.id)
    return render(request, 'core/pdf.html', {'pdf_url': document.file.url.replace('study_materials/study_materials/', 'study_materials/')})

