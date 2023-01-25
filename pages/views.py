from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

from django.http import HttpResponse


class HomePageView(TemplateView):
    template_name = 'home.html'

class DashBoardAdmin(TemplateView):
    template_name = 'dashboard.html'

class DashBoardStudent(TemplateView):
    template_name = 'stat.html'

class HomePageViewStudent(TemplateView):
    template_name = 'studenthome.html'