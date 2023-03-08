from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings


app_name = 'pages'

urlpatterns = [
   path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
   path('admin/', views.HomePageView.as_view(), name='admin'),
   path('admin/dashboard/', views.DashBoardAdmin.as_view(), name='dashboard'),
   path('admin/dashboard/searchrecord/', views.SearchRecord.as_view(), name='searchrecord'),
   path('admin/dashboard/updaterecord/', views.UpdateRecord.as_view(), name='updaterecord'),
   path('admin/dashboard/deleterecord/', views.DeleteRecord.as_view(), name='deleterecord'),
   path('admin/dashboard/managereport/', views.ManageReport.as_view(), name='managereport'),
   path('dashboard/', views.StudentDashboard.as_view(), name='studentdashboard'),
   path('dashboardout/', views.StudentDashboardOut.as_view(), name='studentdashboardout'),
   path('tablesample/', views.TableSample.as_view(), name='tablesample'),
   path('visitor/', views.VisitorDashboard.as_view(), name='visitordashboard'),
   path('visitor/about/', views.AboutUs.as_view(), name='aboutus'),
   path('', views.VisitorLoginPage.as_view(), name='stat'),
   path('logout_view/', views.logout_view, name='logout_view'),
   path('systemadminprofile/', views.SystemAdminProfile.as_view(), name='sysadminprofile'),


]