# admins/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AdminRegistrationForm, AdminLoginForm
from .models import Admin
from students.models import Student
from trainers.models import Trainer
from vehicles.models import Vehicle,VehicleAssignmentHistory,MaintenanceRecord

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and hasattr(user, 'admin'):
                login(request, user)
                return redirect('admins:admin_dashboard')  # ✅ Correct
            else:
                messages.error(request, 'Invalid admin credentials')
    else:
        form = AdminLoginForm()
    return render(request, 'admins/login.html', {'form': form})

@login_required
def admin_logout(request):
    logout(request)
    return redirect('admins:admin_login')

@login_required
def admin_dashboard(request):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You are not authorized to access the admin dashboard.")
        return redirect('accounts:home')  # redirect to home or login

    student_count = Student.objects.count()
    trainer_count = Trainer.objects.count()
    vehicle_count = Vehicle.objects.count()

    context = {
        'student_count': student_count,
        'trainer_count': trainer_count,
        'vehicle_count': vehicle_count,
    }
    return render(request, 'admins/dashboard.html', context)


@login_required
def manage_students(request):
    if not hasattr(request.user, 'admin'):
        return redirect('home')
        
    students = Student.objects.all()
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) | 
            Q(user__email__icontains=search_query)  |
            Q(student_type__icontains=search_query)
        )
    
    return render(request, 'admins/manage_students.html', {
        'students': students,
    })

from django.db.models import Q  

@login_required
def manage_trainers(request):
    if not hasattr(request.user, 'admin'):
        return redirect('home')
        
    trainers = Trainer.objects.all()
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        trainers = trainers.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) | 
            Q(user__email__icontains=search_query) | 
            Q(specialization__icontains=search_query)
        )
    
    return render(request, 'admins/manage_trainers.html', {
        'trainers': trainers,
    })

@login_required
def manage_vehicles(request):
    if not hasattr(request.user, 'admin'):
        return redirect('home')
        
    vehicles = Vehicle.objects.all()
    return render(request, 'admins/manage_vehicles.html', {'vehicles': vehicles})

@login_required
def add_admin(request):
    # Only primary admin can add another admin
    if not hasattr(request.user, 'admin') or not request.user.admin.is_primary:
        return redirect('admins:admin_dashboard')
        
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Admin.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                is_primary=form.cleaned_data['is_primary']
            )
            messages.success(request, 'New admin created successfully')
            return redirect('admins:admin_dashboard')  # ✅
    else:
        form = AdminRegistrationForm()
    return render(request, 'admins/add_admin.html', {'form': form})

# 🚀 Admin-triggered session assignment view
from students.models import StudentPackage
from students.utils import assign_sessions  # import your session assigning logic

@login_required
def assign_sessions_view(request, pk):
    if not hasattr(request.user, 'admin'):
        messages.error(request, "🚫 You are not authorized to assign sessions.")
        return redirect('admins:admin_dashboard')

    package = get_object_or_404(StudentPackage, pk=pk)

    if not package.payment_status:
        messages.warning(request, "⏳ Payment not completed. Cannot assign sessions.")
    else:
        try:
            assign_sessions(package)
            messages.success(request, f"✅ Sessions successfully assigned for {package.student}")
        except Exception as e:
            messages.error(request, f"❌ Error while assigning sessions: {e}")

    return redirect('admins:manage_students')  # or wherever you're managing student packages


from .forms import VehicleForm, MaintenanceRecordForm, VehicleAssignmentForm
from django.utils import timezone
@login_required
def manage_vehicles(request):
    """View for listing all vehicles"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
        
    vehicles = Vehicle.objects.all().order_by('-created_at')
    return render(request, 'admins/manage_vehicles.html', {'vehicles': vehicles})

@login_required
def add_vehicle(request):
    """View for adding a new vehicle"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.vehicle_number} added successfully.")
            return redirect('admins:manage_vehicles')
    else:
        form = VehicleForm()
        
    return render(request, 'admins/vehicle_form.html', {
        'form': form,
        'title': 'Add New Vehicle'
    })

@login_required
def edit_vehicle(request, vehicle_id):
    """View for editing an existing vehicle"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f"Vehicle {vehicle.vehicle_number} updated successfully.")
            return redirect('admins:manage_vehicles')
    else:
        form = VehicleForm(instance=vehicle)
        
    return render(request, 'admins/vehicle_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Edit Vehicle'
    })

@login_required
def delete_vehicle(request, vehicle_id):
    """View for deleting a vehicle"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        vehicle_number = vehicle.vehicle_number
        vehicle.delete()
        messages.success(request, f"Vehicle {vehicle_number} deleted successfully.")
        return redirect('admins:manage_vehicles')
        
    return render(request, 'admins/confirm_delete.html', {
        'vehicle': vehicle,
        'title': 'Delete Vehicle'
    })

@login_required
def vehicle_detail(request, vehicle_id):
    """View for showing vehicle details"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    maintenance_records = vehicle.maintenance_records.all().order_by('-maintenance_date')
    assignment_history = vehicle.assignment_history.all().order_by('-assigned_date')
    current_trainer = vehicle.get_current_trainer()
    
    context = {
        'vehicle': vehicle,
        'maintenance_records': maintenance_records,
        'assignment_history': assignment_history,
        'current_trainer': current_trainer,
        'is_maintenance_due': vehicle.is_maintenance_due(),
        'days_to_maintenance': vehicle.days_to_maintenance(),
    }
    
    return render(request, 'admins/vehicle_detail.html', context)

@login_required
def add_maintenance_record(request, vehicle_id):
    """View for adding a maintenance record to a vehicle"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance_record = form.save(commit=False)
            maintenance_record.vehicle = vehicle
            maintenance_record.save()
            messages.success(request, "Maintenance record added successfully.")
            return redirect('admins:vehicle_detail', vehicle_id=vehicle.id)
    else:
        initial_data = {'odometer_reading': vehicle.odometer_reading, 'maintenance_date': timezone.now().date()}
        form = MaintenanceRecordForm(initial=initial_data)
        
    return render(request, 'admins/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Add Maintenance Record'
    })

@login_required
def assign_vehicle(request, vehicle_id):
    """View for assigning a vehicle to a trainer"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    current_assignment = vehicle.assignment_history.filter(returned_date__isnull=True).first()
    
    if request.method == 'POST':
        form = VehicleAssignmentForm(request.POST)
        if form.is_valid():
            try:
                assignment = form.save(commit=False)
                assignment.vehicle = vehicle
                assignment.save()
                messages.success(request, f"Vehicle assigned to {assignment.trainer} successfully.")
                return redirect('admins:vehicle_detail', vehicle_id=vehicle.id)
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('admins:assign_vehicle', vehicle_id=vehicle.id)
    else:
        initial_data = {'assigned_date': timezone.now().date()}
        form = VehicleAssignmentForm(initial=initial_data)
        
    return render(request, 'admins/vehicle_assignment_form.html', {
        'form': form,
        'vehicle': vehicle,
        'current_assignment': current_assignment,
        'title': 'Assign Vehicle'
    })

@login_required
def return_vehicle(request, assignment_id):
    """View for marking a vehicle as returned"""
    if not hasattr(request.user, 'admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    assignment = get_object_or_404(VehicleAssignmentHistory, id=assignment_id)
    
    if assignment.returned_date:
        messages.error(request, "This vehicle has already been returned.")
        return redirect('admins:vehicle_detail', vehicle_id=assignment.vehicle.id)
    
    if request.method == 'POST':
        assignment.returned_date = timezone.now().date()
        assignment.notes = request.POST.get('notes', '')
        assignment.save()
        messages.success(request, f"Vehicle returned from {assignment.trainer} successfully.")
        return redirect('admins:vehicle_detail', vehicle_id=assignment.vehicle.id)
        
    return render(request, 'admins/return_vehicle.html', {
        'assignment': assignment,
        'title': 'Return Vehicle'
    })