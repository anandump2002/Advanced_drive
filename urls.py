from django.urls import path
from . import views

urlpatterns = [
    # Vehicle management
    path('', views.vehicle_list, name='vehicle_list'),
    path('create/', views.vehicle_create, name='vehicle_create'),
    path('<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('<int:vehicle_id>/update/', views.vehicle_update, name='vehicle_update'),
    path('<int:vehicle_id>/delete/', views.vehicle_delete, name='vehicle_delete'),
    
    # Maintenance management
    path('maintenance/', views.maintenance_dashboard, name='maintenance_dashboard'),
    path('<int:vehicle_id>/maintenance/add/', views.maintenance_record_create, name='maintenance_record_create'),
    path('maintenance/<int:record_id>/update/', views.maintenance_record_update, name='maintenance_record_update'),
    
    # Vehicle assignments
    path('<int:vehicle_id>/assign/', views.assign_vehicle, name='assign_vehicle'),
    path('assignment/<int:assignment_id>/return/', views.return_vehicle, name='return_vehicle'),
]