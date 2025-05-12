# admins/urls.py
from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('students/', views.manage_students, name='manage_students'),
    path('trainers/', views.manage_trainers, name='manage_trainers'),
    path('vehicles/', views.manage_vehicles, name='manage_vehicles'),
    path('add-admin/', views.add_admin, name='add_admin'),
    path('assign-sessions/<int:pk>/', views.assign_sessions_view, name='assign_sessions'),
    path('vehicles/add/', views.add_vehicle, name='add_vehicle'),
    path('vehicles/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:vehicle_id>/edit/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicles/<int:vehicle_id>/delete/', views.delete_vehicle, name='delete_vehicle'),
    
    # Vehicle maintenance
    path('vehicles/<int:vehicle_id>/maintenance/add/', views.add_maintenance_record, name='add_maintenance_record'),
    
    # Vehicle assignment
    path('vehicles/<int:vehicle_id>/assign/', views.assign_vehicle, name='assign_vehicle'),
    path('assignments/<int:assignment_id>/return/', views.return_vehicle, name='return_vehicle'),
]