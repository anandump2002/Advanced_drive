from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about, name='about'),
    path('contact_us/', views.contact, name='contact'),
    path('courses/', views.available_courses, name='courses'),
    path('', views.home, name='home'),
]
