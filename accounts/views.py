# accounts/views.py

from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileUpdateForm, UserUpdateForm
from .models import UserProfile
from students.models import Course
from students.models import Student

def register_view(request):
    """View for user registration"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Advanced Motor Driving School.')
            if user_profile.user_type == 'student':
                return redirect('students:dashboard')
            elif user_profile.user_type == 'trainer':
                return redirect('trainers:dashboard')
            else:
                return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def get_user_role(user):
    if hasattr(user, 'admin'):
        return 'admin'
    elif hasattr(user, 'trainer'):
        return 'trainer'
    elif hasattr(user, 'student'):
        return 'student'
    return 'guest'

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')

                role = get_user_role(user)
                if role == 'admin':
                    return redirect('admins:admin_dashboard')
                elif role == 'trainer':
                    return redirect('trainers:trainer_dashboard')
                elif role == 'student':
                    return redirect('students:student_dashboard')
                else:
                    return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """View for user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

from django.utils import timezone
from students.models import TrainingSession  # replace with your correct app name & model

@login_required
def profile_view(request):
    """View for user profile"""
    user = request.user

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileUpdateForm(instance=user.profile)

    # Fix: get the Student instance
    upcoming_sessions = []
    if user.profile.user_type == 'student':
        try:
            student = Student.objects.get(user=user)
            upcoming_sessions = TrainingSession.objects.filter(
                student=student,
                session_date__gte=timezone.now().date()
            ).order_by('session_date')
        except Student.DoesNotExist:
            upcoming_sessions = []

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'upcoming_sessions': upcoming_sessions,
    }

    return render(request, 'profile.html', context)

from django.shortcuts import render

def about(request):  
    return render(request, 'about.html')

def home(request):
    courses = Course.objects.all()
    return render(request, 'home.html', {'courses': courses})


def contact(request):  
    return render(request, 'contact.html')


def available_courses(request):
    print("🔍 DEBUG: available_courses view is executing...")
    
    courses = Course.objects.prefetch_related('packages').all()
    
    print(f"📢 Found {courses.count()} courses")
    for course in courses:
        print(f"✅ Course: {course.title}, Packages: {list(course.packages.all())}")
    
    return render(request, "students/courses.html", {"courses": courses}) # Temporary response for testing


