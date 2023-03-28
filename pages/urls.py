from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'pages'

urlpatterns = [
   path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
   path('admin/', views.HomePageView.as_view(), name='admin'),
   path('admin', views.HomePageView.as_view(), name='admin'),
   path('admin/dashboard/', views.DashBoardAdmin.as_view(), name='dashboard'),
   path('admin/dashboard', views.DashBoardAdmin.as_view(), name='dashboard'),
   path('admin/dashboard/searchrecord/', views.SearchRecord.as_view(), name='searchrecord'),
   path('admin/dashboard/searchrecord', views.SearchRecord.as_view(), name='searchrecord'),
   path('admin/dashboard/updaterecord/', views.UpdateRecord.as_view(), name='updaterecord'),
   path('admin/dashboard/updaterecord', views.UpdateRecord.as_view(), name='updaterecord'),
   path('admin/dashboard/deleterecord/', views.DeleteRecord.as_view(), name='deleterecord'),
   path('admin/dashboard/deleterecord', views.DeleteRecord.as_view(), name='deleterecord'),
   path('admin/dashboard/managereport/', views.ManageReport.as_view(), name='managereport'),
   path('admin/dashboard/managereport', views.ManageReport.as_view(), name='managereport'),
   path('dashboard/', views.StudentDashboard.as_view(), name='studentdashboard'),
   path('dashboard', views.StudentDashboard.as_view(), name='studentdashboard'),
   path('dashboardout/', views.StudentDashboardOut.as_view(), name='studentdashboardout'),
   path('dashboardout', views.StudentDashboardOut.as_view(), name='studentdashboardout'),
   path('visitor/', views.VisitorDashboard.as_view(), name='visitordashboard'),
   path('visitor', views.VisitorDashboard.as_view(), name='visitordashboard'),
   path('visitor/about/', views.AboutUs.as_view(), name='aboutus'),
   path('visitor/about', views.AboutUs.as_view(), name='aboutus'),
   path('', views.VisitorLoginPage.as_view(), name='stat'),
   path('logout_view/', views.logout_view, name='logout_view'),
   path('logout_view', views.logout_view, name='logout_view'),
   path('sysadprofile/settings', views.SystemAdminProfile.as_view(), name='sysadprofile'),
   path('sysadprofile/settings/', views.SystemAdminProfile.as_view(), name='sysadprofile'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
