from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College, Department, UserType, DatesLogin, Transactions
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.http import JsonResponse
from django.db.models.functions import Lower, Upper, Substr
from django.forms.models import model_to_dict
import os
import base64
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import csv
from django.db import connection
# from flask import Flask, request, render_template

# app = Flask(__name__)
now = datetime.now()
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

    def __init__(self):
        self.transactions = Transactions.objects.all()

    def get(self, request):
        return render(request, 'dashboard.html', {'transact': self.transactions})
        

class StudentDashboardOut(LoginRequiredMixin, TemplateView):
    template_name = 'dashboardout.html'

    def post(self, request):
        student_id = request.POST['student_id']
        try:
            userinfo = DatesLogin.objects.get(user = student_id, time_out=None)
            
            userinfo.time_out = now.time().replace(second=0, microsecond=0) 
            userinfo.save()
            messages.success(request, ("You have successfully been logged out. Thank you for using our service."))
            return redirect('/dashboardout/')	
        except:
            messages.success(request, ("You didn't log in!"))
            return redirect('/dashboardout/')	


class SystemAdminProfile(LoginRequiredMixin, TemplateView):
    template_name = 'sysadprofile.html'

    def post(self, request):
        if request.POST['username_admin']:
            admin_user = AdminUser.objects.get(pk=1)
            admin_user.admin_username = request.POST['username_admin']
            admin_user.admin_password = request.POST['password_admin']
            admin_user.save()
            messages.success(request, ("Username and Password Changed!"))  
            return render(request, 'sysadprofile.html')
        elif request.POST['username1']:
            admin_user = AdminUser.objects.get(pk=2)
            admin_user.admin_username = request.POST['username_admin1']
            admin_user.admin_password = request.POST['password_admin1']
            admin_user.save()
            messages.success(request, ("Username and Password Changed!"))  
            return render(request, 'sysadprofile.html')
    

class StudentDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'studentdashboard.html'

    def __init__(self):
        self.dept = Department.objects.all()

    def post(self, request):
        student_id = request.POST['student_id']
        try:
            userinfo = UserInfo.objects.get(user_idno = student_id)
            
            DatesLogin.objects.create(dates=now.date(), time_in=now.time().replace(second=0, microsecond=0), time_out=None, user=userinfo.user_idno)
            messages.success(request, ("Succesfully Recorded!"))
            return render(request, 'studentdashboard.html', {'student_id': student_id, 'userinfo':userinfo})
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

class VisitorDashboard(TemplateView):
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
                report_title = f"Add a college named {college}."
            
                Transactions.objects.create(dates=now.date(), title=report_title)
                messages.success(request, ("New College is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('new_college_name'):
            new_college_name = request.POST['new_college_name']
            college_name = request.POST['college_name']
            if college_name != new_college_name:
                college_check = College.objects.get(college_name = college_name)
                college_check.college_name = new_college_name
                college_check.save()
                report_title = f"Updated a college named {college_name} to {new_college_name}."
            
                Transactions.objects.create(dates=now.date(), title=report_title)
                messages.success(request, ("The College Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("College Name is the same with the old one!"))
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('delete_college'):
            college_name = request.POST['delete_college']
            college_check = College.objects.get(college_name = college_name)
            college_check.delete()
            report_title = f"Deleted a college named {college_name}."
            
            Transactions.objects.create(dates=now.date(), title=report_title)
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
                report_title = f"Add a new department {dept}."
            
                Transactions.objects.create(dates=now.date(), title=report_title)
                messages.success(request, ("New Department is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('new_dept_name'):
            new_department_name = request.POST['new_dept_name']
            department_name = request.POST['update_dept_form']
            if department_name != new_department_name:
                dept_check = Department.objects.get(department_name = department_name)
                dept_check.department_name = new_department_name
                dept_check.save()
                report_title = f"Updated the department {department_name} to {new_department_name}"
            
                Transactions.objects.create(dates=now.date(), title=report_title)
                messages.success(request, ("The Department Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("Departname Name is the same with the old one!"))
                return redirect('/admin/dashboard/updaterecord/')	

        elif request.POST.get('delete_dept'):
            department_name = request.POST['delete_dept']
            dept_check = Department.objects.get(department_name = department_name)
            dept_check.delete()
            report_title = f"Deleted the department {department_name}"
            
            Transactions.objects.create(dates=now.date(), title=report_title)
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

                report_title = f"Add a new usertype, {usertype}"
            
                Transactions.objects.create(dates=now.date(), title=report_title)
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('idnum'):
            idnum = request.POST['idnum']
            fname = request.POST['fname']
            mname = request.POST['mname']
            lname = request.POST['lname']
            gender = request.POST['gender']
            dept_select = request.POST['data_list']
            course = request.POST['courses']
            usertype = request.POST['usertype_select']
            comments = request.POST['comments']
            picture = request.FILES['picture']
            try: 
                user_check = UserInfo.objects.get(user_idno = idnum)
                messages.success(request, ("User is Already Registered!"))
                return redirect('/admin/dashboard/updaterecord/')	
            except:
                dept_check = Department.objects.get(department_name = dept_select)
                usertype = UserType.objects.get(type_id = usertype)
                UserInfo.objects.create(user_idno=idnum, image=picture, first_name=fname, middle_name=mname, last_name=lname, gender=gender, comment=comments, course=course, department=dept_check, type=usertype)
                userinfo = UserInfo.objects.get(user_idno = idnum)
                current_filename = userinfo.image.name

                # Define the new filename
                new_filename = f"{idnum}{current_filename[current_filename.rfind('.'):]}"

                # Get the full path of the current file in the media folder
                current_path = os.path.join(settings.MEDIA_ROOT, current_filename)

                # Get the full path of the new file in the media folder
                new_path = os.path.join(settings.MEDIA_ROOT, new_filename)

                # Rename the file
                os.rename(current_path, new_path)
                userinfo.image.name = new_filename
                userinfo.save()
                report_title = f"Import a user data with an ID Number {idnum}"
            
                Transactions.objects.create(dates=now.date(), title=report_title)
                messages.success(request, ("New User is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('input_user_samp'):
            user_searched = request.POST.get('input_user_samp')
            user_searched_details = UserInfo.objects.get(user_idno=user_searched)
            try:
                image_url = user_searched_details.image.url
            except:
                image_url = ""

            user_details = model_to_dict(user_searched_details)
            user_details.pop('image', None)
            return JsonResponse({'user_searched': user_details, 
                                'department':user_searched_details.department.department_name,
                                'usertype': user_searched_details.type.type_name,
                                'image_url': image_url})
        elif request.POST.get('idnum-update'):
            idnum = request.POST['idnum-update']
            fname = request.POST['fname-update']
            mname = request.POST['mname-update']
            lname = request.POST['lname-update']
            gender = request.POST['gender-update']
            dept_select = request.POST['data_list1']
            course = request.POST['courses-update']
            usertype = request.POST['usertype_select-update']
            comments = request.POST['comments-update']
            picture = request.FILES['picture1']
    
            user_check = UserInfo.objects.get(user_idno = idnum)
            file_path_delete = user_check.image.path

            # Delete the file
            os.remove(file_path_delete)
            dept_check = Department.objects.get(department_name = dept_select)
            usertype = UserType.objects.get(type_id = usertype)
            user_check.user_idno = idnum
            user_check.image = picture
            user_check.first_name = fname
            user_check.middle_name = mname
            user_check.last_name = lname
            user_check.gender = gender
            user_check.comment = comments
            user_check.course = course
            user_check.department = dept_check
            user_check.type = usertype
            user_check.save()
            userinfo = UserInfo.objects.get(user_idno = idnum)
            current_filename = userinfo.image.name

            # Define the new filename
            new_filename = f"{idnum}{current_filename[current_filename.rfind('.'):]}"

            # Get the full path of the current file in the media folder
            current_path = os.path.join(settings.MEDIA_ROOT, current_filename)

            # Get the full path of the new file in the media folder
            new_path = os.path.join(settings.MEDIA_ROOT, new_filename)

            # Rename the file
            os.rename(current_path, new_path)
            userinfo.image.name = new_filename
            userinfo.save()
            report_title = f"Updated a user data with an ID Number {idnum}"
            
            Transactions.objects.create(dates=now.date(), title=report_title)
            messages.success(request, ("The data has been updated!"))	
            return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('confirmation1'):
            id_delete = request.POST['idnum-delete']
            user_check = UserInfo.objects.get(user_idno=id_delete)
            user_check.delete()
            user_check_logins = DatesLogin.objects.get(user=id_delete)
            user_check_logins.delete()
            report_title = f"Deleted a user with a ID Number {id_delete}"
            
            Transactions.objects.create(dates=now.date(), title=report_title)
            
            messages.success(request, ("Record Deleted!"))
            return redirect('/admin/dashboard/updaterecord/')
        elif request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']
            # Read the CSV file
            csv_data = csv_file.read().decode('utf-8').splitlines()
            # Create a CSV reader object
            reader = csv.reader(csv_data)
            # Skip the header row
            next(reader)
            # Insert data into the database
            with connection.cursor() as cursor:
                for row in reader:
                    users = UserInfo(user_idno=row[0], first_name=row[1], middle_name=row[2], last_name=row[3], gender=row[4],
                                    course=row[5], comment=row[6], type_id=row[7], department_id=row[8])
                    users.save()
            
            Transactions.objects.create(dates=now.date(), title="Batch Import Users!")
            messages.success(request, "Users are Registered!")
            return redirect('/admin/dashboard/updaterecord/')

        
class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

    def post(self, request):
        if request.POST.get('confirmation'):
            start_date = datetime.strptime(request.POST['start_date1'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date1'], '%m/%d/%Y')
            dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date])
            dates_login.delete()
            report_title = f"Deleted a records from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}"
            
            Transactions.objects.create(dates=now.date(), title=report_title)
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
        self.start_date = ""
        self.end_date = ""
        self.start_time = ""
        self.end_time = ""
        
    def get(self, request):
        return render(request, 'manageReport.html', {'usertype': self.usertype})
    def post(self, request):
        def report_check(user_type, dates_login):
            tempObject = []
            check_user_type = UserType.objects.filter(type_name=user_type)
            if check_user_type.exists():
                for item in dates_login:
                    usertype_query = UserType.objects.get(type_name__iexact=user_type)
                    user_query = UserInfo.objects.get(user_idno=item.user, type_id=usertype_query.type_id)
                    if user_query:
                        data = {'department': user_query.department.department_name, 'college': user_query.department.college.college_name}
                        tempObject.append(data)
                department_counts = {}
                for item in tempObject:
                    department = item['department']
                    college = item['college']
                    if department not in department_counts:
                        department_counts[department] = {}
                    if college not in department_counts[department]:
                        department_counts[department][college] = 0
                    department_counts[department][college] += 1
                return department_counts
            else:
                for item in dates_login:
                    user_query = UserInfo.objects.get(user_idno=item.user)
                    if user_query:
                        data = {'Department': user_query.department.department_name, 'College': user_query.department.college.college_name, 'month_name': user_type}
                    return data
        def csvfile(tempObject, semesters):
            data_dict = {}
            for obj in tempObject:
                dept = obj['Department']
                college = obj['College']
                month = obj['month_name']
                key = f'{dept}_{college}'
                if key not in data_dict:
                    if semesters == "intersession":
                        data_dict[key] = {'Department': dept, 'College': college, 'June': 0, 'July': 0, 'Overall': 0}
                    elif semesters == "first_sem":
                        data_dict[key] = {'Department': dept, 'College': college, 'August': 0, 'September': 0, 'October': 0, 'November': 0, 'December': 0, 'Overall': 0}
                    else:
                        data_dict[key] = {'Department': dept, 'College': college, 'January': 0, 'February': 0, 'March': 0, 'April': 0, 'May': 0, 'Overall': 0}
                data_dict[key][month] += 1
                data_dict[key]['Overall'] += 1
            
            return data_dict

        if request.POST.get('schoolyear'):
            start_year_report = request.POST['start-year-report']
            end_year_report = request.POST['end-year-report']
            jan_login = DatesLogin.objects.none()
            feb_login = DatesLogin.objects.none()
            march_login = DatesLogin.objects.none()
            april_login = DatesLogin.objects.none()
            may_login = DatesLogin.objects.none()
            june_login = DatesLogin.objects.none()
            july_login = DatesLogin.objects.none()
            aug_login = DatesLogin.objects.none()
            sept_login = DatesLogin.objects.none()
            oct_login = DatesLogin.objects.none()
            nov_login = DatesLogin.objects.none()
            dec_login = DatesLogin.objects.none()
            if request.POST['schoolyear'] == 'intersession':
                semester = "Intersession"
                for year in range(int(start_year_report), int(end_year_report) + 1):
                    qs = DatesLogin.objects.filter(dates__range=[datetime.strptime('06/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('06/30/'+str(year), '%m/%d/%Y').date()])
                    qs1 = DatesLogin.objects.filter(dates__range=[datetime.strptime('07/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('07/31/'+str(year), '%m/%d/%Y').date()])
                    june_login = june_login | qs 
                    july_login = july_login | qs1
                final_array = []
                for query in june_login:
                    final_array.append(report_check("June", june_login))
                for query in july_login:
                    final_array.append(report_check("July", july_login))
                output = csvfile(final_array, 'intersession')
            elif request.POST['schoolyear'] == 'firstsem':
                semester = "First Semester"
                for year in range(int(start_year_report), int(end_year_report) + 1):
                    qs = DatesLogin.objects.filter(dates__range=[datetime.strptime('08/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('08/31/'+str(year), '%m/%d/%Y').date()])
                    qs1 = DatesLogin.objects.filter(dates__range=[datetime.strptime('09/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('09/30/'+str(year), '%m/%d/%Y').date()])
                    qs2 = DatesLogin.objects.filter(dates__range=[datetime.strptime('10/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('10/31/'+str(year), '%m/%d/%Y').date()])
                    qs3 = DatesLogin.objects.filter(dates__range=[datetime.strptime('11/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('11/30/'+str(year), '%m/%d/%Y').date()])
                    qs4 = DatesLogin.objects.filter(dates__range=[datetime.strptime('12/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('12/31/'+str(year), '%m/%d/%Y').date()])
                    aug_login = aug_login | qs 
                    sept_login = sept_login | qs1
                    oct_login = oct_login | qs2
                    nov_login = nov_login | qs3
                    dec_login = dec_login | qs4
                final_array = []
                for query in aug_login:
                    final_array.append(report_check("August", aug_login))
                for query in sept_login:
                    final_array.append(report_check("September", sept_login))
                for query in oct_login:
                    final_array.append(report_check("October", oct_login))
                for query in nov_login:
                    final_array.append(report_check("November", nov_login))
                for query in dec_login:
                    final_array.append(report_check("December", dec_login))
                output = csvfile(final_array, 'first_sem')
            else: 
                semester = "Second Semester"
                for year in range(int(start_year_report), int(end_year_report) + 1):
                    qs = DatesLogin.objects.filter(dates__range=[datetime.strptime('01/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('01/31/'+str(year), '%m/%d/%Y').date()])
                    if year % 4 == 0:
                        qs1 = DatesLogin.objects.filter(dates__range=[datetime.strptime('02/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('02/29/'+str(year), '%m/%d/%Y').date()])
                    else: 
                        qs1 = DatesLogin.objects.filter(dates__range=[datetime.strptime('02/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('02/28/'+str(year), '%m/%d/%Y').date()])
                    qs2 = DatesLogin.objects.filter(dates__range=[datetime.strptime('03/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('03/31/'+str(year), '%m/%d/%Y').date()])
                    qs3 = DatesLogin.objects.filter(dates__range=[datetime.strptime('04/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('04/30/'+str(year), '%m/%d/%Y').date()])
                    qs4 = DatesLogin.objects.filter(dates__range=[datetime.strptime('05/01/'+str(year), '%m/%d/%Y').date(), datetime.strptime('05/31/'+str(year), '%m/%d/%Y').date()])
                    jan_login = jan_login | qs 
                    feb_login = feb_login | qs1
                    march_login = march_login | qs2
                    april_login = april_login | qs3
                    may_login = may_login | qs4
                final_array = []
                for query in jan_login:
                    final_array.append(report_check("January", jan_login))
                for query in feb_login:
                    final_array.append(report_check("February", feb_login))
                for query in march_login:
                    final_array.append(report_check("March", march_login))
                for query in april_login:
                    final_array.append(report_check("April", april_login))
                for query in may_login:
                    final_array.append(report_check("May", may_login))
                output = csvfile(final_array, 'second_sem')
            
            if bool(output):
                Transactions.objects.create(dates=now.date(), title="Generated Report from "+semester+" year "+start_year_report+" to "+end_year_report+".")
            return JsonResponse({'final_output':output})
        elif request.POST.get('exportIndividualUsers'):
            
            start_time = datetime.strptime(request.POST['start_time_report'], '%I:%M %p')
            end_time = datetime.strptime(request.POST['end_time_report'], '%I:%M %p')
            start_date = datetime.strptime(request.POST['start_date_report'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date_report'], '%m/%d/%Y')

            report_title = f"Extracted a {request.POST['kind_of_report']} report of {request.POST['report_for_user']} visits from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')} from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}."

            Transactions.objects.create(dates=now.date(), title=report_title)
            return JsonResponse({'success': True})
        else:
            user_type = request.POST['name']
            start_time =  datetime.strptime(request.POST['start-time-'+user_type], '%H:%M')
            end_time =  datetime.strptime(request.POST['end-time-'+user_type], '%H:%M')
            start_date = datetime.strptime(request.POST['start-date-'+user_type], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end-date-'+user_type], '%m/%d/%Y')
            dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date], time_in__range=[start_time, end_time], time_out__range=[start_time, end_time])
            tempObject = report_check(user_type, dates_login)
            return JsonResponse ({'start_date': start_date, 'start_time': start_time, 'end_date': end_date, 'end_time':end_time, 'data':tempObject})


class TableSample(LoginRequiredMixin, TemplateView):
    template_name = 'tablesample.html'

class AboutUs(LoginRequiredMixin, TemplateView):
    template_name = 'aboutus.html'