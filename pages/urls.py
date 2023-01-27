from django.urls import path
from . import views


app_name = 'pages'

urlpatterns = [
   path('admin/', views.HomePageView.as_view(), name='admin'),
   path('admin/dashboard/', views.DashBoardAdmin.as_view(), name='dashboard'),
   path('admin/dashboard/searchrecord/', views.SearchRecord.as_view(), name='searchrecord'),
   path('admin/dashboard/updaterecord/', views.UpdateRecord.as_view(), name='updaterecord'),
   path('admin/dashboard/deleterecord/', views.DeleteRecord.as_view(), name='deleterecord'),
   path('admin/dashboard/managereport/', views.ManageReport.as_view(), name='managereport'),
   path('', views.DashBoardStudent.as_view(), name='stat'),
]