from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College
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
        data = AdminUser.objects.all()
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

class DashBoardAdmin(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

class VisitorLoginPage(TemplateView):
    template_name = 'stat.html'
    
    def __init__(self):
        try:
            self.adminId = AdminUser.objects.get(admin_id=1)
        except: 
            AdminUser.objects.create(admin_id=1, admin_username="jobladmin", admin_password="jobl123")

class Sidebar(TemplateView):
    template_name = 'sidebar.html'

class SearchRecord(LoginRequiredMixin, TemplateView):
    template_name = 'searchRecord.html'

class UpdateRecord(LoginRequiredMixin, TemplateView):
    template_name = 'updateRecord.html'
    # def get(self, request):
    #     college = request.GET['college']
    #     print(college)
    def __init__(self):
        self.colleges = College.objects.all()

    def get(self, request):
        return render(request, 'updateRecord.html', {'data': self.colleges})

    def post(self, request):
        college = request.POST['college']
        try: 
            college_check = College.objects.get(college_name = college)
            messages.success(request, ("College is Already Registered!"))
            return redirect('/admin/dashboard/updaterecord/')	
        except:
             College.objects.create(college_id=self.colleges.count(), college_name=college)
             messages.success(request, ("New College is Registered!"))	
             return redirect('/admin/dashboard/updaterecord/')	

        # user = UserInfo.objects.get(idnum=idnum)
        # if user is not None:
        #     messages.success(request, ("User already registered!"))	
        #     return redirect('/admin/dashboard/updaterecord/')	
        # else:
        #     print(idnum)

class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

class ManageReport(LoginRequiredMixin, TemplateView):
    template_name = 'manageReport.html'