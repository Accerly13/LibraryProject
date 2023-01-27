from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from .models import Admins
import pyautogui as pag

# Create your views here.

from django.http import HttpResponse


def checkAccount(request): 
    admin_username = Admins.objects.all()
    return admin_username[0].admin_username

class HomePageView(TemplateView):
    template_name = 'home.html'
            
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

