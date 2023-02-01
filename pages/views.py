from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
import pyautogui as pag
from .models import Admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse


@login_required
def protected_view(request):
    # Your protected view logic here
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('http://127.0.0.1:8000/admin/')

class HomePageView(TemplateView):
    def get(self, request):
        data = Admin.objects.all()
        return render(request, 'home.html', {'data': data})
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard/')
        else:
            messages.success(request, ("Invalid Username or Password!"))	
            return redirect('/admin/')	
    # def get(request):
    #         return render(request, 'home.html', {})

class DashBoardAdmin(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

class VisitorLoginPage(TemplateView):
    template_name = 'stat.html'
    adminId = Admin.objects.get(admin_id=1)
    if adminId is None:
        Admin.objects.create(admin_id=1, admin_username="jobladmin", admin_password="jobl123")

class Sidebar(TemplateView):
    template_name = 'sidebar.html'

class SearchRecord(LoginRequiredMixin, TemplateView):
    template_name = 'searchRecord.html'

class UpdateRecord(LoginRequiredMixin, TemplateView):
    template_name = 'updateRecord.html'
    def post(self, request):
        idnum = request.POST['idnum']
        fname = request.POST['fname']
        user = Admin.objects.get(idnum=idnum)
        if user is not None:
            messages.success(request, ("User already registered!"))	
            return redirect('/admin/dashboard/updaterecord/')	
        else:
            print(idnum)

class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

class ManageReport(LoginRequiredMixin, TemplateView):
    template_name = 'manageReport.html'