from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College, Department, UserType, Course, DatesLogin
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
        try:
            userinfo = UserInfo.objects.get(idnum = student_id)
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
        # if (self.usertype.count() == 0): 
        #     UserType.objects.create(usertype_id=1, usertype_name="Student")
        #     UserType.objects.create(usertype_id=2, usertype_name="Faculty")
        #     UserType.objects.create(usertype_id=3, usertype_name="Personnel")
        #     UserType.objects.create(usertype_id=4, usertype_name="Visitor")
        # if (self.colleges.count() == 0):
        #     College.objects.create(college_id = 1, college_name='College of Arts & Sciences')
        #     College.objects.create(college_id = 2, college_name='College of Business and Accountancy')
        #     College.objects.create(college_id = 3, college_name='College of Computer Studies')
        #     College.objects.create(college_id = 4, college_name='College of Education')
        #     College.objects.create(college_id = 5, college_name='College of Engineering')
        #     College.objects.create(college_id = 6, college_name='College of Nursing')
        #     College.objects.create(college_id = 7, college_name='Graduate School')
        #     College.objects.create(college_id = 8, college_name=' ')
        #     College.objects.create(college_id = 9, college_name='Senior High G11')
        #     College.objects.create(college_id = 10, college_name='College of Law')
        #     College.objects.create(college_id = 11, college_name='Senior High GTwelve')
        # if (self.dept.count() == 0):
        #     Department.objects.create(dept_id = 1, department_name='Department of Literature and Language Studies', college_id=1)
        #     Department.objects.create(dept_id = 2, department_name='Department of Mathematics', college_id=1),
        #     Department.objects.create(dept_id = 3, department_name='Department of Media Studies', college_id=1),
        #     Department.objects.create(dept_id = 4, department_name='Department of Natural Sciences', college_id=1),
        #     Department.objects.create(dept_id = 5, department_name='Department of Philosophy', college_id=1),
        #     Department.objects.create(dept_id = 6, department_name='Department of Psychology', college_id=1),
        #     Department.objects.create(dept_id = 7, department_name='Department of Social Sciences', college_id=1),
        #     Department.objects.create(dept_id = 8, department_name='AS-F', college_id=1),
        #     Department.objects.create(dept_id = 9, department_name='Department of Accountancy', colelge_id=2),
        #     Department.objects.create(dept_id = 10, department_name='Department of Allied Business Courses', college_id=2),
        #     Department.objects.create(dept_id = 11, department_name='Department of Business Management Courses', college_id=2),
        #     Department.objects.create(dept_id = 12, department_name='Department of Financial Management Courses', college_id=2),
        #     Department.objects.create(dept_id = 13, department_name='CBA-F', college_id=2),
        #     Department.objects.create(dept_id = 14, department_name='Department of Computer Science', college_id=3),
        #     Department.objects.create(dept_id = 2, department_name='Department of Digital Arts and Computer Animation', college_id=3),
        #     Department.objects.create(dept_id = 2, department_name='CS-F', college_id=3),
        #     Department.objects.create(dept_id = 2, department_name='Department of Education', 40),
        #     Department.objects.create(dept_id = 2, department_name='Education-F', 40),
        #     Department.objects.create(dept_id = 2, department_name='Department of Civil Engineering', 50),
        #     Department.objects.create(dept_id = 2, department_name='Department of Electronics and Computer Engineering', 50),
        #     Department.objects.create(dept_id = 2, department_name='Department of ECE', 50),
        #     Department.objects.create(dept_id = 2, department_name='Enggineering-F', 50),
        #     Department.objects.create(dept_id = 2, department_name='Department of Nursing', 60),
        #     Department.objects.create(dept_id = 2, department_name='Nursing-F', 60),
        #     Department.objects.create(dept_id = 2, department_name='Graduate School', 70),
        #     Department.objects.create(dept_id = 2, department_name='GradSchool-F', 70),
        #     Department.objects.create(dept_id = 2, department_name='Unidentified', 80),
        #     Department.objects.create(dept_id = 2, department_name='PERSONNEL', 80),
        #     Department.objects.create(dept_id = 2, department_name='ATTC', 80),
        #     Department.objects.create(dept_id = 2, department_name='Cross Enrollee', 80),
        #     Department.objects.create(dept_id = 2, department_name='NSTP/CFFP', 80),
        #     Department.objects.create(dept_id = 2, department_name='High School', 80),
        #     Department.objects.create(dept_id = 2, department_name='Pre School', 80),
        #     Department.objects.create(dept_id = 2, department_name='ICTC', 80),
        #     Department.objects.create(dept_id = 2, department_name='SLP', 80),
        #     Department.objects.create(dept_id = 2, department_name='Department of Theology', 10),
        #     Department.objects.create(dept_id = 2, department_name='Department of Computer Engineering Technology', 50),
        #     Department.objects.create(dept_id = 2, department_name='Degree Holder', 80),
        #     Department.objects.create(dept_id = 2, department_name='Department of Religious Education', 10),
        #     Department.objects.create(dept_id = 2, department_name='HUMSS', 90),
        #     Department.objects.create(dept_id = 2, department_name='ABM', 90),
        #     Department.objects.create(dept_id = 2, department_name='STEM', 90),
        #     Department.objects.create(dept_id = 2, department_name='GA', 90),
        #     Department.objects.create(dept_id = 2, department_name='AVFX', 90),
        #     Department.objects.create(dept_id = 2, department_name='SocJourn', 90),
        #     Department.objects.create(dept_id = 2, department_name='TAP', 90),
        #     Department.objects.create(dept_id = 2, department_name='Department of CMA', 20),
        #     Department.objects.create(dept_id = 2, department_name='SJ', 20),
        #     Department.objects.create(dept_id = 2, department_name='ABM T', 110),
        #     # (107, 'STEM T', 110),
        #     # (108, 'AVFX T', 110),
        #     # (109, 'HUMSS T', 110),
        #     # (110, 'SOCJOURN T', 110),
        #     # (111, 'TAP T', 110),
        #     # (112, 'GA T', 110),
        #     # (114, 'College of Law', 100),
        #     # (115, 'AS Communication', 10),
        #     # (116, 'Department of Political Science', 10),
        #     # (117, 'Department of Entrepreneurship', 20),
        #     # (118, 'Department of Banking and Finance', 20),
        #     # (119, 'Department of Marketing Management', 10),
        #     # (120, 'Department of Tourism Management', 10),
        #     # (121, 'Department of Environmental Management', 10),
        #     # (122, 'Department of CPE', 50);
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
                dept_check = Department.objects.get(department_name = dept_select)
                usertype = UserType.objects.get(usertype_name = usertype)
                try:
                    course_check = Course.objects.get(course_name = course)
                except:
                    Course.objects.create(course_id=self.course.count(), course_name=course, department=dept_check)
                    course_check = Course.objects.get(course_name = course)
                UserInfo.objects.create(idnum=idnum, fname=fname, mname=mname, lname=lname, gender=gender, comment=comments, course=course_check, dept=dept_check, usertype=usertype)
                messages.success(request, ("New User is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	       
        elif request.POST.get('user_update'):
            usertype = request.POST['user_update']
            try: 
                users = UserInfo.objects.filter(idnum__startswith=usertype)
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