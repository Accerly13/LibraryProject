from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import AdminUser, UserInfo, College, Department, UserType, DatesLogin, Transactions, Visitors, Course
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.db.models.functions import Lower, Upper, Substr
from django.forms.models import model_to_dict
import os
import base64
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import csv
from django.templatetags.static import static
from django.db import connection

media_root = settings.MEDIA_ROOT
static_root = settings.STATIC_ROOT
media_url = settings.MEDIA_URL


file_list = os.listdir(media_root)
now = datetime.now()
@login_required
def protected_view(request):
    # Your protected view logic here
    return render(request, 'stat.html')

def logout_view(request):
    logout(request)
    return redirect('/admin/')

class HomePageView(TemplateView):
    def get(self, request):
        try:
            AdminUser.objects.get(pk=1)
        except:
            AdminUser.objects.create_superuser(admin_id=1, username="jobladmin", password="jobl123")
        data = AdminUser.objects.all()
        return render(request, 'home.html', {'data': data})
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.admin_id == 1:
            login(request, user)
            return redirect('/admin/dashboard/')
        else:
            messages.success(request, ("Invalid Username or Password!"))	
            return redirect('/admin/')	

class DashBoardAdmin(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def __init__(self):
        self.transactions = Transactions.objects.all()

    def get(self, request):
        return render(request, 'dashboard.html', {'transact': self.transactions})
    
    def post(self, request):
        dates_delete = datetime.strptime(request.POST['date-delete'], '%B %d, %Y')
        transact_delete = Transactions.objects.filter(dates=dates_delete)
        transact_delete.delete()
        
        return render(request, 'dashboard.html')
        

class StudentDashboardOut(LoginRequiredMixin, TemplateView):
    template_name = 'dashboardout.html'

    def post(self, request):
        student_id = request.POST['student_id']
        try:
            userinfo_check = UserInfo.objects.get(Q(user_idno=student_id) | Q(alternative_id=student_id))
            dates_check = DatesLogin.objects.get(user=userinfo_check.user_idno, time_out=None)
            dates_check.time_out = now.time().replace(second=0, microsecond=0) 
            dates_check.save()
            messages.success(request, ("You have successfully been logged out. Thank you for using our service."))
            return redirect('/dashboardout/')	
        except:
            messages.success(request, ("You didn't log in!"))
            return redirect('/dashboardout/')	


class SystemAdminProfile(LoginRequiredMixin, TemplateView):
    template_name = 'sysadprofile.html'

    def post(self, request):
        try: 
            admin_user = AdminUser.objects.get(pk=1)
            admin_user.username = request.POST['username_admin']
            admin_user.set_password(request.POST['password_admin'])
            admin_user.save()
            messages.success(request, ("Username and Password Changed!"))  
            return render(request, 'sysadprofile.html')
        except:
            admin_user = AdminUser.objects.get(pk=2)
            admin_user.username = request.POST['username_admin1']
            admin_user.set_password(request.POST['password_admin1'])
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
            userinfo_check = UserInfo.objects.get(Q(user_idno=student_id) | Q(alternative_id=student_id))
            try:
                image_url = userinfo_check.image.url
            except:
                filename = userinfo_check.user_idno+".png"
                if os.path.isfile(os.path.join(media_root, filename)):
                    if filename.endswith('.jpg') or filename.endswith('.png'):
                        file_path = os.path.join(media_url, filename)
                        image_url = file_path
                else:
                    image_url = "/avatar.svg"
                
            user_details = model_to_dict(userinfo_check)
            user_details.pop('image', None)
            try:
                dates_check = DatesLogin.objects.get(user=userinfo_check.user_idno, time_out=None)
                dates_check.time_out = datetime.strptime('17:00:00', '%H:%M:%S')
                dates_check.save()
                DatesLogin.objects.create(dates=now.date(), time_in=now.time().replace(second=0, microsecond=0), time_out=None, user=userinfo_check.user_idno)
                messages.success(request, ("Successfully recorded! Please log out next time"))
                return render(request, 'studentdashboard.html', {'student_id': student_id, 'userinfo':user_details, 'notLogout': True, 'img_url':image_url,
                                                                'department': userinfo_check.department.department_name, 'course':userinfo_check.course.course_name,
                                                                'comment':userinfo_check.comment})
            except:
                DatesLogin.objects.create(dates=now.date(), time_in=now.time().replace(second=0, microsecond=0), time_out=None, user=userinfo_check.user_idno)
                messages.success(request, ("Succesfully Recorded!"))
                return render(request, 'studentdashboard.html', {'student_id': student_id, 'userinfo':user_details, 'img_url':image_url,
                                                                 'department': userinfo_check.department.department_name, 'course':userinfo_check.course.course_name,
                                                                 'comment':userinfo_check.comment})
        except Exception as e:
            print(str(e))
            messages.success(request, ("We're sorry, but we couldn't find your account in our database"))
            return render(request, 'studentdashboard.html', {'student_id': student_id})

class VisitorDashboard(TemplateView):
    template_name = 'visitordashboard.html'

    def post(self, request):
        school = request.POST['nameOfSchool']
        purpose = request.POST['visitPurpose']
        name = request.POST['visitorName']
        email = request.POST['emailAddress']
        phone = request.POST['phoneNumber']
        student_id = request.POST['studentId']
        Visitors.objects.create(dates=now.date(), time=now.time().replace(second=0, microsecond=0), school=school, purpose=purpose,
                                name=name, email=email, phone=phone, student_id=student_id)
        messages.success(request, ("Succesfully Recorded!"))
        return render(request, 'visitordashboard.html')

class VisitorLoginPage(TemplateView):
    template_name = 'stat.html'
    
    def __init__(self):
        try:
            AdminUser.objects.get(pk=2)
        except:
            AdminUser.objects.create_superuser(admin_id=2, username="user", password="jobl123")
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.admin_id == 2:
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
        if self.usertype.count() == 0:
            UserType.objects.create(type_id=1, type_name='FACULTY')
            UserType.objects.create(type_id=2, type_name='PERSONNEL')
            UserType.objects.create(type_id=3, type_name='STUDENT')
            UserType.objects.create(type_id=4, type_name='VISITOR')
        
        self.usertype = UserType.objects.all()
        self.users = UserInfo.objects.all().annotate(firstname=Lower('first_name')).order_by('last_name')
        self.course = Course.objects.all()
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
                report_title = f"Added a new college, '{college}'."
            
                Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
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
            
                Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
                messages.success(request, ("The College Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("College Name is the same with the old one!"))
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('delete_college'):
            college_name = request.POST['delete_college']
            print(college_name)
            college_check = College.objects.get(college_name = college_name)
            if request.POST['confirmation-college'] == "Yes":
                college_check.delete()
                report_title = f"Deleted a college named {college_name}."
                
                Transactions.objects.create(dates=now.date(), title=report_title, transact="delete")
                messages.success(request, ("Deleted!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                dept_check = Department.objects.filter(college_id=college_check.college_id)
            
                departments_of_this_college = {'departments': list(dept_check.values())}
                return JsonResponse({'departments_of_this_college': departments_of_this_college, 'college_delete': college_name })
        elif request.POST.get('colleges-inputs'):
            return_message = False
            colleges = request.POST.get('colleges-inputs').split("\n")
            if colleges[-1] == "":
                colleges.pop()
            # Remove newlines from college names
            colleges = [college.rstrip() for college in colleges]
            for college in colleges:
                existing_college_names = [college.college_name for college in College.objects.all()]
                if college in existing_college_names:
                    return_message = True
                else:
                    College.objects.create(college_name=college)
            if return_message == False:
                messages.success(request, ("New Colleges are Registered!"))
            else:
                messages.success(request, ("Other colleges are already registered but those who were not registered yet we've been register thru it."))
            report_title = f"Batch Add Colleges Manually."
            Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
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
                report_title = f"Added a new department, '{dept}'."
            
                Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
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
            
                Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
                messages.success(request, ("The Department Name is Changed!"))
                return redirect('/admin/dashboard/updaterecord/')	
            else:
                messages.success(request, ("Departname Name is the same with the old one!"))
                return redirect('/admin/dashboard/updaterecord/')	

        elif request.POST.get('delete_dept'):
            department_name = request.POST['delete_dept']
            dept_check = Department.objects.get(department_name = department_name)
            if request.POST['confirmation-department'] == "Yes":
                dept_check.delete()
                report_title = f"Deleted the department {department_name}"
                
                Transactions.objects.create(dates=now.date(), title=report_title, transact="delete")
                messages.success(request, ("Deleted!"))
                return redirect('/admin/dashboard/updaterecord/')
            else:
                users = UserInfo.objects.filter(department_id=dept_check.department_id)
        
                users_in_this_department = {'users': list(users.values())}
                return JsonResponse({'users_in_this_department': users_in_this_department, 'department_delete': department_name })
        elif request.POST.get('department-inputs'):
            return_message = False
            departments = request.POST.get('department-inputs').split("\n")
            if departments[-1] == "":
                departments.pop()
            # Remove newlines from college names
            departments = [department.rstrip() for department in departments]
            
            college_check = College.objects.get(college_name=request.POST['from_college'])
            for department in departments:
                existing_department_names = [department.department_name for department in Department.objects.all()]
                if department in existing_department_names:
                    return_message = True
                else:
                    Department.objects.create(department_name=department, college=college_check)
            if return_message == False:
                messages.success(request, ("New Departments are Registered!"))
            else:
                messages.success(request, ("Other departments are already registered but those who were not registered yet we've been register thru it."))
            report_title = f"Batch Add Departments Manually."
            Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
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

                report_title = f"Added a new usertype, '{usertype}'."
            
                Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
                return redirect('/admin/dashboard/updaterecord/')	
        elif request.POST.get('idnum'):
            idnum = request.POST['idnum']
            fname = request.POST['fname']
            if request.POST['altid']:
                altid = request.POST['altid']
            else:
                altid = ''
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
                try:
                    course_check = Course.objects.get(course_name = course)
                except:
                    course_check = Course.objects.create(course_name = course, department = dept_check)
                    course_check.save()
                
                usertype = UserType.objects.get(type_id = usertype)
                UserInfo.objects.create(user_idno=idnum, alternative_id=altid, image=picture, first_name=fname, middle_name=mname, last_name=lname, gender=gender, comment=comments, course_id=course_check.course_id, department=dept_check, type=usertype)
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
            
                Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
                messages.success(request, ("New User is Registered!"))	
                return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('input_user_samp'):
            user_searched = request.POST.get('input_user_samp')
            user_searched_details = UserInfo.objects.get(user_idno=user_searched)
            try:
                image_url = user_searched_details.image.url
            except:
                try:
                    filename = user_searched+".png"
                    if os.path.isfile(os.path.join(media_root, filename)):
                        if filename.endswith('.jpg') or filename.endswith('.png'):
                            file_path = os.path.join(media_url, filename)
                            image_url = file_path
                    else:
                        image_url = "/avatar.svg"
                except:
                    filename = user_searched+".jpg"
                    if os.path.isfile(os.path.join(media_root, filename)):
                        if filename.endswith('.jpg') or filename.endswith('.png'):
                            file_path = os.path.join(media_url, filename)
                            image_url = file_path
                    else:
                        image_url = "/avatar.svg"



            user_details = model_to_dict(user_searched_details)
            user_details.pop('image', None)
            return JsonResponse({'user_searched': user_details, 
                                'department':user_searched_details.department.department_name,
                                'usertype': user_searched_details.type.type_id,
                                'image_url': image_url})
        elif request.POST.get('idnum-update'):
            idnum = request.POST['idnum-update']
            fname = request.POST['fname-update']
            mname = request.POST['mname-update']
            lname = request.POST['lname-update']
            gender = request.POST['gender-update']
            if request.POST['alt-id-update']:
                altid = request.POST['alt-id-update']
            else:
                altid = ''
            dept_select = request.POST['data_list1']
            course = request.POST['courses-update']
            usertype = request.POST['usertype_select-update']
            comments = request.POST['comments-update']
            user_check = UserInfo.objects.get(user_idno = idnum)
            try:
                picture = request.FILES['picture1']
                try:
                    file_path_delete = user_check.image.path
                    # Delete the file
                    os.remove(file_path_delete)
                except Exception as e:
                    # Print the error message to the console
                    print('An error occurred:', str(e))
                user_check.image = picture
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
            except Exception as e:
                # Print the error message to the console
                print('An error occurred:', str(e))
                

            dept_check = Department.objects.get(department_name = dept_select)
            usertype = UserType.objects.get(type_id = usertype)
            try: 
                course_check = Course.objects.get(course_name = course)
            except:
                course_check = Course.objects.create(course_name = course, department=dept_check)
                course_check.save()
            user_check.user_idno = idnum
            user_check.first_name = fname
            user_check.middle_name = mname
            user_check.last_name = lname
            user_check.gender = gender
            user_check.comment = comments
            user_check.course = course_check
            user_check.department = dept_check
            user_check.type = usertype
            user_check.alternative_id = altid
            user_check.save()
            report_title = f"Updated a user data with an ID Number {idnum}"
            
            Transactions.objects.create(dates=now.date(), title=report_title, transact="update")
            messages.success(request, ("The data has been updated!"))	
            return redirect('/admin/dashboard/updaterecord/')
        elif request.POST.get('confirmation1'):
            id_delete = request.POST['idnum-delete']
            user_check = UserInfo.objects.get(user_idno=id_delete)
            try:
                file_path_delete = user_check.image.path
                os.remove(file_path_delete)
            except:
                try:
                    file_path_delete =  media_root+"\/"+id_delete+".png"
                    os.remove(file_path_delete)
                except:
                    try:
                        file_path_delete =  media_root+"\/"+id_delete+".jpg"
                        os.remove(file_path_delete)
                    except:
                        print("Deleted!")

            # Delete the file
            user_check.delete()
            user_check_logins = DatesLogin.objects.filter(user=id_delete)
            user_check_logins.delete()
            report_title = f"Deleted a user with a ID Number {id_delete}"
            
            Transactions.objects.create(dates=now.date(), title=report_title, transact="delete")
            
            messages.success(request, ("Record Deleted!"))
            return redirect('/admin/dashboard/updaterecord/')
        else:
            try:
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
                          
                        existing_user_idnos = [user.user_idno for user in UserInfo.objects.all()]

                        existing_alternative_id = [user.alternative_id for user in UserInfo.objects.all()]
                        if row[0] in existing_user_idnos:
                            continue
                         
                        if row[9] in existing_alternative_id:
                            continue

                        try:
                            course_create = Course.objects.get(course_name=row[5])
                           
                        except:
                            course_create = Course.objects.create(course_name=row[5], department_id=row[8])
                            course_create.save()
    
                        users = UserInfo.objects.create(user_idno=row[0], first_name=row[1], middle_name=row[2], last_name=row[3], gender=row[4],
                                    course_id=course_create.course_id, comment=row[6], type_id=row[7], department_id=row[8], alternative_id=row[9])
                        users.save()
                            

                Transactions.objects.create(dates=now.date(), title="Uploaded a CSV file for User batch upload.", transact="update")
                messages.success(request, "Users are Registered!")
                return redirect('/admin/dashboard/updaterecord/')
            except:
                try:
                    csv_file = request.FILES['csv_file1']
                # Read the CSV file
                    csv_data = csv_file.read().decode('utf-8').splitlines()
                    # Create a CSV reader object
                    reader = csv.reader(csv_data)
                    # Skip the header row
                    next(reader)
                    # Insert data into the database
                    
                    with connection.cursor() as cursor:
                        for row in reader:
                            existing_college = [colleges.college_id for colleges in College.objects.all()]
                            if row[0] in existing_college:
                                continue
                            college = College(college_id=row[0], college_name=row[1])
                            college.save()
                    
                    Transactions.objects.create(dates=now.date(), title="Uploaded a CSV file for College batch upload.", transact="update")
                    messages.success(request, "Colleges are Registered!")
                    return redirect('/admin/dashboard/updaterecord/')
                except: 
                    csv_file = request.FILES['csv_file2']
                    # Read the CSV file
                    csv_data = csv_file.read().decode('utf-8').splitlines()
                    # Create a CSV reader object
                    reader = csv.reader(csv_data)
                    # Skip the header row
                    next(reader)
                   
                    with connection.cursor() as cursor:
                        for row in reader:
                            existing_departments = [departments.department_id for departments in Department.objects.all()]
                            if row[0] in existing_departments:
                                continue
                            department = Department(department_id=row[0], department_name=row[1], college_id=row[2])
                            department.save()
                    
                    Transactions.objects.create(dates=now.date(), title="Uploaded a CSV file for Department batch upload.", transact="update")
                    messages.success(request, "Departments are Registered!")
                    return redirect('/admin/dashboard/updaterecord/')
        
class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

    def post(self, request):
        if request.POST.get('confirmation'):
            start_date = datetime.strptime(request.POST['start_date1'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date1'], '%m/%d/%Y')
            dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date])
            dates_login.delete()
            report_title = f"Deleted records from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}"
            
            Transactions.objects.create(dates=now.date(), title=report_title, transact="delete")
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
                Transactions.objects.create(dates=now.date(), title="Generated Report from "+semester+" year "+start_year_report+" to "+end_year_report+".", transact="manage")
            return JsonResponse({'final_output':output})
        elif request.POST.get('exportIndividualUsers'):
            
            start_time = datetime.strptime(request.POST['start_time_report'], '%I:%M %p')
            end_time = datetime.strptime(request.POST['end_time_report'], '%I:%M %p')
            start_date = datetime.strptime(request.POST['start_date_report'], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end_date_report'], '%m/%d/%Y')

            report_title = f"Extracted a {request.POST['kind_of_report']} report of {request.POST['report_for_user']} visits from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')} from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}."

            Transactions.objects.create(dates=now.date(), title=report_title, transact="manage")
            return JsonResponse({'success': True})
        else:
            user_type = request.POST['name']
            start_time =  datetime.strptime(request.POST['start-time-'+user_type], '%H:%M')
            end_time =  datetime.strptime(request.POST['end-time-'+user_type], '%H:%M')
            start_date = datetime.strptime(request.POST['start-date-'+user_type], '%m/%d/%Y')
            end_date = datetime.strptime(request.POST['end-date-'+user_type], '%m/%d/%Y')
            if user_type == 'visitor':
                visitor_login = Visitors.objects.filter(dates__range=[start_date, end_date], time__range=[start_time, end_time])

                user_logins = {'visitor_login': list(visitor_login.values())}
                return JsonResponse ({'start_date': start_date, 'start_time': start_time, 'end_date': end_date, 'end_time':end_time, 'data':user_logins})
            else:
                dates_login = DatesLogin.objects.filter(dates__range=[start_date, end_date], time_in__range=[start_time, end_time], time_out__range=[start_time, end_time])
                tempObject = report_check(user_type, dates_login)
                return JsonResponse ({'start_date': start_date, 'start_time': start_time, 'end_date': end_date, 'end_time':end_time, 'data':tempObject})


class TableSample(LoginRequiredMixin, TemplateView):
    template_name = 'tablesample.html'

class AboutUs(LoginRequiredMixin, TemplateView):
    template_name = 'aboutus.html'