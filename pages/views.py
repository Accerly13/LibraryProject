from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
import pyautogui as pag
from .models import Admins
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse

@login_required
def protected_view(request):
    # Your protected view logic here
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('admin')

class HomePageView(TemplateView):
    template_name = 'home.html'
    def get(self, request):
        data = Admins.objects.all()
        return render(request, 'home.html', {'data': data})

class DashBoardAdmin(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def tryLang(message):
        pag.alert(message)

class VisitorLoginPage(LoginRequiredMixin, TemplateView):
    template_name = 'stat.html'

class Sidebar(TemplateView):
    template_name = 'sidebar.html'

class SearchRecord(LoginRequiredMixin, TemplateView):
    template_name = 'searchRecord.html'

class UpdateRecord(LoginRequiredMixin, TemplateView):
    template_name = 'updateRecord.html'

class DeleteRecord(LoginRequiredMixin, TemplateView):
    template_name = 'deleteRecord.html'

class ManageReport(LoginRequiredMixin, TemplateView):
    template_name = 'manageReport.html'

