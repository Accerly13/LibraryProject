from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College, Department, UserType, DatesLogin, Course
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime


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

class StudentDashboardOut(LoginRequiredMixin, TemplateView):
    template_name = 'dashboardout.html'

class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'studentdashboard.html'

    def post(self, request):
        student_id = request.POST['student_id']
        print(student_id)
        try:
            userinfo = UserInfo.objects.get(user_idno = student_id)
            now = datetime.now()
            DatesLogin.objects.create(dates=now.date(), time_in=now.time(), time_out=None, user=userinfo)
            messages.success(request, ("Succesfully Recorded!"))
            return redirect('/dashboard/')	
        except:
            messages.success(request, ("Intruder Alert!"))
            return redirect('/dashboard/')	

        # try: 
        #     college_check = College.objects.get(college_name = college)
        #     messages.success(request, ("College is Already Registered!"))
        #     return redirect('/admin/dashboard/updaterecord/')	
        # except:
        #     College.objects.create(college_name=college)
        #     messages.success(request, ("New College is Registered!"))	
        #     return redirect('/admin/dashboard/updaterecord/')	

class VisitorDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'visitordashboard.html'
class VisitorLoginPage(TemplateView):
    template_name = 'stat.html'
    
    def __init__(self):
        try:
            self.adminId = AdminUser.objects.get(admin_id=1)
        except: 
            AdminUser.objects.create(admin_id=1, admin_username="jobladmin", admin_password="jobl123")
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard/')
        else:
            messages.success(request, ("Invalid Username or Password!"))	
            return redirect('/')

class Sidebar(TemplateView):
    template_name = 'sidebar.html'

class SearchRecord(LoginRequiredMixin, TemplateView):
    template_name = 'searchRecord.html'

class UpdateRecord(LoginRequiredMixin, TemplateView):
    template_name = 'updateRecord.html'
    def __init__(self):
        self.colleges = College.objects.all()
        self.dept = Department.objects.all()
        self.usertype = UserType.objects.all()
        self.course = Course.objects.all()
    def get(self, request):
        return render(request, 'updateRecord.html', {'data': self.colleges, 'dept': self.dept, 'usertype': self.usertype, 'course': self.course})

    def post(self, request):
        if request.POST.get('college'):
            college = request.POST['college']
            try: 
                college_check = College.objects.get(college_name = college)
                messages.success(request, ("College is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                College.objects.create(college_name=college)
                messages.success(request, ("New College is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('new_college_name'):
            new_college_name = request.POST['new_college_name']
            college_name = request.POST['college_name']
            if college_name != new_college_name:
                college_check = College.objects.get(college_name = college_name)
                college_check.college_name = new_college_name
                college_check.save()
                messages.success(request, ("The College Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("Pareho man lang, inedit mo pa!"))
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('delete_college'):
            college_name = request.POST['delete_college']
            college_check = College.objects.get(college_name = college_name)
            college_check.delete()
            messages.success(request, ("Deleted!"))
            return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('dept'):
            dept = request.POST['dept']
            college_name = request.POST['from_college']
            try: 
                dept_check = Department.objects.get(department_name = dept)
                messages.success(request, ("Department is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                college_check = College.objects.get(college_name = college_name)
                Department.objects.create(department_name=dept, college=college_check)
                messages.success(request, ("New Department is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('new_department_name'):
            new_department_name = request.POST['new_department_name']
            department_name = request.POST['update_dept_form']
            if department_name != new_department_name:
                dept_check = Department.objects.get(department_name = department_name)
                dept_check.department_name = new_department_name
                dept_check.save()
                messages.success(request, ("The Department Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("Pareho man lang, inedit mo pa!"))
                return redirect('/admin/dashboard/updaterecord/')	

        elif request.POST.get('delete_dept'):
            department_name = request.POST['delete_dept']
            dept_check = Department.objects.get(department_name = department_name)
            dept_check.delete()
            messages.success(request, ("Deleted!"))
            return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('usertype'):
            usertype = request.POST['usertype']
            try: 
                usertype_check = UserType.objects.get(type_name = usertype)
                messages.success(request, ("Usertype is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                UserType.objects.create(type_id=self.usertype.count()+1, type_name=usertype)
                messages.success(request, ("New Usertype is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('idnum'):
            idnum = request.POST['idnum']
            fname = request.POST['fname']
            mname = request.POST['mname']
            lname = request.POST['lname']
            gender = request.POST['gender']
            dept_select = request.POST['department_select']
            course = request.POST['courses']
            usertype = request.POST['usertype_select']
            comments = request.POST['comments']
            print(course)
            try: 
                user_check = UserInfo.objects.get(user_idno = idnum)
                messages.success(request, ("User is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                dept_check = Department.objects.get(department_name = dept_select)
                usertype = UserType.objects.get(type_id = usertype)
                try:
                    course_check = Course.objects.get(course_name = course)
                except:
                    Course.objects.create(course_id=self.course.count(), course_name=course, department=dept_check)
                    course_check = Course.objects.get(course_name = course)
                UserInfo.objects.create(user_idno=idnum, first_name=fname, middle_name=mname, last_name=lname, gender=gender, comment=comments, course_user=course_check, course="", department=dept_check, type=usertype)
                messages.success(request, ("New User is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	       
        elif request.POST.get('user_update'):
            usertype = request.POST['user_update']
            try: 
                users = UserInfo.objects.filter(user_idno__startswith=usertype)
                messages.success(request, ("Usertype is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                messages.success(request, ("New Usertype is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	     
        
class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

class ManageReport(LoginRequiredMixin, TemplateView):
    template_name = 'manageReport.html'

class TableSample(LoginRequiredMixin, TemplateView):
    template_name = 'tablesample.html'