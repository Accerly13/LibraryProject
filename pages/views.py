from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College, Department, UserType, Course
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

class StudentDashboardOut(LoginRequiredMixin, TemplateView):
    template_name = 'dashboardout.html'

class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'studentdashboard.html'

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
        if (self.usertype.count() == 0): 
            UserType.objects.create(usertype_id=1, usertype_name="Student")
            UserType.objects.create(usertype_id=2, usertype_name="Faculty")
            UserType.objects.create(usertype_id=3, usertype_name="Personnel")
            UserType.objects.create(usertype_id=4, usertype_name="Visitor")

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
                College.objects.create(college_id=self.colleges.count(), college_name=college)
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
                dept_check = Department.objects.get(dept_name = dept)
                messages.success(request, ("Department is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                college_check = College.objects.get(college_name = college_name)
                Department.objects.create(department_id=self.dept.count(), dept_name=dept, college=college_check)
                messages.success(request, ("New Department is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('new_dept_name'):
            new_dept_name = request.POST['new_dept_name']
            dept_name = request.POST['update_dept_form']
            if dept_name != new_dept_name:
                dept_check = Department.objects.get(dept_name = dept_name)
                dept_check.dept_name = new_dept_name
                dept_check.save()
                messages.success(request, ("The Department Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("Pareho man lang, inedit mo pa!"))
                return redirect('/admin/dashboard/updaterecord/')	

        elif request.POST.get('delete_dept'):
            dept_name = request.POST['delete_dept']
            dept_check = Department.objects.get(dept_name = dept_name)
            dept_check.delete()
            messages.success(request, ("Deleted!"))
            return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('usertype'):
            usertype = request.POST['usertype']
            try: 
                usertype_check = UserType.objects.get(usertype_name = usertype)
                messages.success(request, ("Usertype is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                UserType.objects.create(usertype_id=self.usertype.count()+1, usertype_name=usertype)
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
            if course == "":
                course = request.POST['courses1']
            usertype = request.POST['usertype_select']
            comments = request.POST['comments']
            
            try: 
                user_check = UserInfo.objects.get(idnum = idnum)
                messages.success(request, ("User is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                dept_check = Department.objects.get(dept_name = dept_select)
                usertype = UserType.objects.get(usertype_name = usertype)
                try:
                    course_check = Course.objects.get(course_name = course)
                except:
                    Course.objects.create(course_id=self.course.count(), course_name=course, department=dept_check)
                    course_check = Course.objects.get(course_name = course)
                UserInfo.objects.create(idnum=idnum, fname=fname, mname=mname, lname=lname, gender=gender, comment=comments, course=course_check, dept=dept_check, usertype=usertype)
                messages.success(request, ("New User is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	            
        
class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

class ManageReport(LoginRequiredMixin, TemplateView):
    template_name = 'manageReport.html'

class TableSample(LoginRequiredMixin, TemplateView):
    template_name = 'tablesample.html'