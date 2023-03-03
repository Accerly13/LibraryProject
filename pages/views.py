from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College, Department, UserType, DatesLogin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
from django.db.models.functions import Lower, Upper, Substr
from django.forms.models import model_to_dict


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

    def post(self, request):
        student_id = request.POST['student_id']
        try:
            userinfo = DatesLogin.objects.get(user = student_id, time_out=None)
            now = datetime.now()
            userinfo.time_out = now.time().replace(second=0, microsecond=0) 
            userinfo.save()
            messages.success(request, ("You have successfully been logged out. Thank you for using our service."))
            return redirect('/dashboardout/')	
        except:
            messages.success(request, ("You didn't log in!"))
            return redirect('/dashboardout/')	

class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'studentdashboard.html'

    def __init__(self):
        self.dept = Department.objects.all()
        self.users = UserInfo.objects.all()

    def post(self, request):
        student_id = request.POST['student_id']
        try:
            userinfo = UserInfo.objects.get(user_idno = student_id)
            now = datetime.now()
            DatesLogin.objects.create(dates=now.date(), time_in=now.time().replace(second=0, microsecond=0), time_out=None, user=userinfo.user_idno)
            messages.success(request, ("Succesfully Recorded!"))
            return render(request, 'studentdashboard.html', {'student_id': student_id, 'users':self.users})
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

    def __init__(self):
        self.dept = Department.objects.all()
        self.users = UserInfo.objects.all().annotate(firstname=Lower('first_name')).order_by('last_name')
        self.dates_login = DatesLogin.objects.all()
    def get(self, request):
        return render(request, 'searchRecord.html', {'dept': self.dept, 'users': self.users, 'dates_login': self.dates_login})
        
    def post(self, request):
        if request.POST.get('input_user_samp'):
            user_searched = request.POST.get('input_user_samp')
            user_searched_dates = DatesLogin.objects.filter(user=user_searched)
            user_logins = {'dates_login': list(user_searched_dates.values())}
            return JsonResponse({'user_searched': user_logins})
        else: 
            start_time =  datetime.strptime(request.POST['start_time'], '%H:%M')
            end_time =  datetime.strptime(request.POST['end_time'], '%H:%M')
            start_date = datetime.strptime(request.POST['start_date'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date'], '%m/%d/%Y')
            tempObject = []
            dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date], time_in__range=[start_time, end_time], time_out__range=[start_time, end_time])
            for item in dates_login:
                user_query = UserInfo.objects.get(user_idno=item.user)
                if user_query:
                    data = {'name': user_query.last_name + ' ' + user_query.first_name + ' ' + user_query.middle_name, 'department': user_query.department.department_name}
                    tempObject.append(data)
            dates_login_context = {'dates_login': list(dates_login.values())}
            return JsonResponse ({'dates_login_searched': dates_login_context , 'start_date': start_date, 'start_time': start_time, 'end_date': end_date, 'end_time':end_time, 'data':tempObject})	

class UpdateRecord(LoginRequiredMixin, TemplateView):
    template_name = 'updateRecord.html'
    def __init__(self):
        self.colleges = College.objects.all()
        self.dept = Department.objects.all()
        self.usertype = UserType.objects.all()
        self.users = UserInfo.objects.all().annotate(firstname=Lower('first_name')).order_by('last_name')
        self.course = UserInfo.objects.values_list('course', flat=True).distinct()
    def get(self, request):
        return render(request, 'updateRecord.html', { 'data': self.colleges, 'dept': self.dept, 'usertype': self.usertype, 'users': self.users, 'course': self.course})

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
            if course == "":
                course = request.POST['courses1']
            usertype = request.POST['usertype_select']
            comments = request.POST['comments']
            try: 
                user_check = UserInfo.objects.get(user_idno = idnum)
                messages.success(request, ("User is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                dept_check = Department.objects.get(department_name = dept_select)
                usertype = UserType.objects.get(type_id = usertype)
                UserInfo.objects.create(user_idno=idnum, first_name=fname, middle_name=mname, last_name=lname, gender=gender, comment=comments, course=course, department=dept_check, type=usertype)
                messages.success(request, ("New User is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('input_user_samp'):
            user_searched = request.POST.get('input_user_samp')
            user_searched_details = UserInfo.objects.get(user_idno=user_searched)
            user_details = model_to_dict(user_searched_details)
            print(user_details)
            return JsonResponse({'user_searched': user_details, 
                                 'department':user_searched_details.department.department_name, 
                                 'college': user_searched_details.department.college.college_name})   

        
class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

    def post(self, request):
        if request.POST.get('confirmation'):
            start_date = datetime.strptime(request.POST['start_date1'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date1'], '%m/%d/%Y')
            dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date])
            dates_login.delete()
            messages.success(request, ("Records Deleted!"))
            return redirect('/admin/dashboard/deleterecord/')
        else:
            start_date = datetime.strptime(request.POST['start_date'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date'], '%m/%d/%Y')
            dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date]).values_list('dates', flat=True).distinct()
            tempObject = []
            for item in dates_login:
                dates_login_filtered = DatesLogin.objects.filter(dates=item)
                data = {'date':item, 'earliest_time':dates_login_filtered.earliest('time_in').time_in, 'latest_time':dates_login_filtered.latest('time_in').time_in,
                        'no_of_user':dates_login_filtered.values_list('user', flat=True).distinct().count()}
                tempObject.append(data)
            return JsonResponse ({'start_date': start_date, 'end_date': end_date, 'data':tempObject})	

class ManageReport(LoginRequiredMixin, TemplateView):
    template_name = 'manageReport.html'

    def __init__(self):
        self.usertype = UserType.objects.all()
        
    def get(self, request):
        return render(request, 'manageReport.html', {'usertype': self.usertype})
    
    def post(self, request):
        user_type = request.POST['name']
        start_time =  datetime.strptime(request.POST['start-time-'+user_type], '%H:%M')
        end_time =  datetime.strptime(request.POST['end-time-'+user_type], '%H:%M')
        start_date = datetime.strptime(request.POST['start-date-'+user_type], '%m/%d/%Y')
        end_date = datetime.strptime(request.POST['end-date-'+user_type], '%m/%d/%Y')
        tempObject = []
        dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date], time_in__range=[start_time, end_time], time_out__range=[start_time, end_time])
        for item in dates_login:
            usertype_query = UserType.objects.get(type_name__iexact=user_type)
            print(usertype_query)
            user_query = UserInfo.objects.get(user_idno=item.user, type_id=usertype_query.type_id)
            if user_query:
                data = {'department': user_query.department.department_name, 'college': user_query.department.college.college_name, 'user':user_query.user_idno}
                tempObject.append(data)
        department_counts = {}
        for item in tempObject:
            department = item['department']
            college = item['college']
            user = item['user']
            if department not in department_counts:
                department_counts[department] = {}
            if college not in department_counts[department]:
                department_counts[department][college] = {}
            if user not in department_counts[department][college]:
                department_counts[department][college][user] = 1
        return JsonResponse ({'start_date': start_date, 'start_time': start_time, 'end_date': end_date, 'end_time':end_time, 'data':department_counts})

class TableSample(LoginRequiredMixin, TemplateView):
    template_name = 'tablesample.html'

class AboutUs(LoginRequiredMixin, TemplateView):
    template_name = 'aboutus.html'