from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import Vehicle, MaintenanceRecord, VehicleAssignmentHistory
from .forms import VehicleForm, MaintenanceRecordForm, VehicleAssignmentForm
from trainers.models import Trainer

@login_required
def vehicle_list(request):
    # Filter options
    vehicle_type = request.GET.get('type')
    status = request.GET.get('status')
    maintenance_due = request.GET.get('maintenance')
    search_query = request.GET.get('search')
    
    vehicles = Vehicle.objects.all()
    
    # Apply filters
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    if status:
        is_active = status == 'active'
        vehicles = vehicles.filter(is_active=is_active)
    if maintenance_due == 'due':
        vehicles = [v for v in vehicles if v.is_maintenance_due()]
    if search_query:
        vehicles = vehicles.filter(
            Q(make__icontains=search_query) | 
            Q(model__icontains=search_query) | 
            Q(vehicle_number__icontains=search_query)
        )
    
    context = {
        'vehicles': vehicles,
        'vehicle_types': Vehicle.VEHICLE_TYPES,
        'current_filters': {
            'type': vehicle_type,
            'status': status,
            'maintenance': maintenance_due,
            'search': search_query
        }
    }
    return render(request, 'vehicles/vehicle_list.html', context)

@login_required
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    maintenance_records = vehicle.maintenance_records.all().order_by('-maintenance_date')
    assignment_history = vehicle.assignment_history.all().order_by('-assigned_date')
    
    context = {
        'vehicle': vehicle,
        'maintenance_records': maintenance_records,
        'assignment_history': assignment_history,
        'is_maintenance_due': vehicle.is_maintenance_due(),
        'days_to_maintenance': vehicle.days_to_maintenance()
    }
    return render(request, 'vehicles/vehicle_detail.html', context)

@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_number} has been created.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = VehicleForm()
    
    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'title': 'Add New Vehicle',
        'button_text': 'Add Vehicle'
    })

@login_required
def vehicle_update(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_number} has been updated.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = VehicleForm(instance=vehicle)
    
    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': f'Edit Vehicle: {vehicle.vehicle_number}',
        'button_text': 'Save Changes'
    })

@login_required
def vehicle_delete(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        vehicle_number = vehicle.vehicle_number
        vehicle.delete()
        messages.success(request, f'Vehicle {vehicle_number} has been deleted.')
        return redirect('vehicle_list')
    
    return render(request, 'vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})

@login_required
def maintenance_record_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST)
        if form.is_valid():
            maintenance_record = form.save(commit=False)
            maintenance_record.vehicle = vehicle
            maintenance_record.save()
            messages.success(request, 'Maintenance record added successfully.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = MaintenanceRecordForm(initial={'odometer_reading': vehicle.odometer_reading})
    
    return render(request, 'vehicles/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': f'Add Maintenance Record for {vehicle}'
    })

@login_required
def maintenance_record_update(request, record_id):
    record = get_object_or_404(MaintenanceRecord, id=record_id)
    vehicle = record.vehicle
    
    if request.method == 'POST':
        form = MaintenanceRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maintenance record updated successfully.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = MaintenanceRecordForm(instance=record)
    
    return render(request, 'vehicles/maintenance_form.html', {
        'form': form,
        'vehicle': vehicle,
        'record': record,
        'title': f'Edit Maintenance Record for {vehicle}'
    })

@login_required
def assign_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = VehicleAssignmentForm(request.POST)
        if form.is_valid():
            trainer = form.cleaned_data['trainer']
            reason = form.cleaned_data['reason']
            
            # Check if vehicle is already assigned
            if vehicle.currently_assigned:
                # Close the previous assignment
                prev_assignment = VehicleAssignmentHistory.objects.filter(
                    vehicle=vehicle, 
                    returned_date=None
                ).first()
                
                if prev_assignment:
                    prev_assignment.returned_date = form.cleaned_data['assigned_date']
                    prev_assignment.save()
            
            # Create new assignment
            assignment = VehicleAssignmentHistory(
                vehicle=vehicle,
                trainer=trainer,
                assigned_date=form.cleaned_data['assigned_date'],
                reason=reason
            )
            assignment.save()
            
            # Update vehicle's current assignment
            vehicle.currently_assigned = trainer
            vehicle.save()
            
            messages.success(request, f'Vehicle successfully assigned to {trainer}.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        form = VehicleAssignmentForm()
    
    return render(request, 'vehicles/assign_vehicle.html', {
        'form': form,
        'vehicle': vehicle
    })

@login_required
def return_vehicle(request, assignment_id):
    assignment = get_object_or_404(VehicleAssignmentHistory, id=assignment_id, returned_date=None)
    vehicle = assignment.vehicle
    
    if request.method == 'POST':
        return_date = request.POST.get('return_date')
        notes = request.POST.get('notes')
        
        assignment.returned_date = return_date
        assignment.notes = notes
        assignment.save()
        
        # Update vehicle's current assignment
        vehicle.currently_assigned = None
        vehicle.save()
        
        messages.success(request, f'Vehicle {vehicle} has been returned.')
        return redirect('vehicle_detail', vehicle_id=vehicle.id)
    
    return render(request, 'vehicles/return_vehicle.html', {
        'assignment': assignment,
        'vehicle': vehicle
    })

@login_required
def maintenance_dashboard(request):
    # Vehicles needing maintenance soon (within next 30 days)
    maintenance_due_vehicles = [v for v in Vehicle.objects.filter(is_active=True) 
                               if v.is_maintenance_due() or (v.days_to_maintenance() and v.days_to_maintenance() <= 30)]
    
    # Recent maintenance records
    recent_records = MaintenanceRecord.objects.all().order_by('-maintenance_date')[:10]
    
    context = {
        'maintenance_due_vehicles': maintenance_due_vehicles,
        'recent_records': recent_records,
    }
    return render(request, 'vehicles/maintenance_dashboard.html', context)