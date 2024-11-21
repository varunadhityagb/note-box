# core/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import CustomUser, Class, ClassEnrollment, StudyMaterials, Doubt, DoubtResponse, TimeBoxedSession
from .forms import TimeBoxedSessionForm, DoubtForm, DoubtResponseForm
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
            return redirect(f"/classes/{class_name}/")
    else:
        form = TimeBoxedSessionForm()

    class_instance = Class.objects.get(name=class_name)
    materials = StudyMaterials.objects.filter(lass_instance=class_instance)
    timeboxed_sessions = TimeBoxedSession.objects.filter(class_instance = class_instance, start_time__lte=timezone.now(), end_time__gte=timezone.now())
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

    doubts_status_wise = (Doubt.objects
                          .filter(study_material=pdf_material)
                          .order_by('status', 'created_at'))
    
    grouped_doubts = {
        'OPEN': [],
        'ANSWERED': [],
        'CLOSED': []
    }

    for doubt in doubts_status_wise:
        grouped_doubts[doubt.status].append(doubt)

    if request.method == 'POST' and not request.user.is_teacher:
        form1 = DoubtForm(request.POST)
        if form1.is_valid():
            doubt = form1.save(commit=False)
            doubt.student = request.user
            doubt.class_instance = class_instance
            doubt.study_material = pdf_material
            doubt.save()
            return redirect(f"/classes/{class_name}/{fileName}/")
    else:
        form1 = DoubtForm()

    if request.method == 'POST':
        form2 = DoubtResponseForm(request.POST)
        if form2.is_valid():
            doubt_response = form2.save(commit=False)
            doubt_response.user = request.user
            doubt_id = request.POST.get('doubt_id')
            doubt_response.doubt = get_object_or_404(Doubt, id=doubt_id)
            doubt_response.save()
            related_doubt = doubt_response.doubt
            if request.user.is_teacher:
                related_doubt.status = 'ANSWERED'
                related_doubt.save()
            return redirect(f"/classes/{class_name}/{fileName}/")
    else:
        form2 = DoubtResponseForm()

    document = get_object_or_404(StudyMaterials, id=pdf_material.id)
    responses = DoubtResponse.objects.filter(doubt__study_material=pdf_material)
    print(response.content for response in responses)
    return render(request, 'core/pdf.html', {'user': request.user,
                                            'pdf_url': document.file.url, 
                                            'grouped_doubts_open':grouped_doubts['OPEN'], 
                                            'grouped_doubts_answered':grouped_doubts['ANSWERED'], 
                                            'grouped_doubts_closed':grouped_doubts['CLOSED'],
                                            'form1':form1, 'form2':form2, 'responses':responses})

def timeboxed_session(request, title):
    if not request.user.is_authenticated:
        return redirect('core:login')
    elif request.user.is_staff:
        return redirect('/admin')
    
    session = get_object_or_404(TimeBoxedSession, title=title)
    return render(request, 'core/timebox.html', {'user': request.user, 'session':session, 'pdf_url': session.study_material.file.url, })