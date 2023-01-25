from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
   path('admin/', views.HomePageView.as_view(), name='admin'),
   path('admin/dashboard', views.DashBoardAdmin.as_view(), name='dashboard'),
   path('', views.HomePageViewStudent.as_view(), name='home'),
   path('studentdashboard/', views.DashBoardStudent.as_view(), name='studentdashboard')
]