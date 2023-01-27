from django.shortcuts import render
from django.views.generic import TemplateView
import pyautogui as pag
from .models import Admins

# Create your views here.

from django.http import HttpResponse


class HomePageView(TemplateView):
    template_name = 'home.html'
    admin_username = Admins.objects.all()
    # pag.alert(admin_username[0].admin_username)
    
        
class DashBoardAdmin(TemplateView):
    template_name = 'dashboard.html'

    def tryLang(message):
        pag.alert(message)

class DashBoardStudent(TemplateView):
    template_name = 'stat.html'

class HomePageViewStudent(TemplateView):
    template_name = 'studenthome.html'

class Sidebar(TemplateView):
    template_name = 'sidebar.html'

class SearchRecord(TemplateView):
    template_name = 'searchRecord.html'

class UpdateRecord(TemplateView):
    template_name = 'updateRecord.html'

class DeleteRecord(TemplateView):
    template_name = 'deleteRecord.html'

class ManageReport(TemplateView):
    template_name = 'manageReport.html'

