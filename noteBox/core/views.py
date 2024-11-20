# core/views.py
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from .forms import CustomLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

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
    return render(request, 'core/classes.html', {'user': request.user})


def smn(req):
    return HttpResponse("OK")