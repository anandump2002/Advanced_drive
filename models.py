from django.db import models
from django.utils import timezone
from trainers.models import Trainer

class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ('CAR', 'Car'),
        ('SCOOTY', 'Scooty'),
        ('OTHER', 'Other'),
        ('HEAVY','HEAVY'),
        ('SCOOTY&CAR','SCOOTY & CAR')
    )

    vehicle_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    purchased_year = models.PositiveIntegerField()

    registration_expiry = models.DateField(null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    seating_capacity = models.PositiveIntegerField(default=2)

    # Maintenance tracking
    last_service_date = models.DateField(null=True, blank=True)
    next_service_due = models.DateField(null=True, blank=True)
    odometer_reading = models.PositiveIntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.vehicle_number})"

    def is_maintenance_due(self):
        if not self.next_service_due:
            return False
        return self.next_service_due <= timezone.now().date()

    def days_to_maintenance(self):
        if not self.next_service_due:
            return None
        delta = self.next_service_due - timezone.now().date()
        return delta.days

    def get_current_trainer(self):
        """Fetch the latest assigned trainer"""
        last_assignment = self.assignment_history.filter(returned_date__isnull=True).order_by('-assigned_date').first()
        return last_assignment.trainer if last_assignment else None


class MaintenanceRecord(models.Model):
    MAINTENANCE_TYPES = (
        ('REGULAR', 'Regular Service'),
        ('REPAIR', 'Repair'),
        ('INSPECTION', 'Inspection'),
        ('OTHER', 'Other')
    )
    
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )
    
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    odometer_reading = models.PositiveIntegerField()
    performed_by = models.CharField(max_length=100)
    
    # For tracking next service
    next_service_due_date = models.DateField(null=True, blank=True)
    next_service_due_km = models.PositiveIntegerField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vehicle} - {self.maintenance_type} on {self.maintenance_date}"
    
    def save(self, *args, **kwargs):
        # Update the vehicle's next service due date when saving a maintenance record
        super().save(*args, **kwargs)
        
        # Update vehicle information if this is the latest maintenance
        latest_record = MaintenanceRecord.objects.filter(
            vehicle=self.vehicle
        ).order_by('-maintenance_date', '-created_at').first()
        
        if latest_record == self:
            self.vehicle.last_service_date = self.maintenance_date
            self.vehicle.next_service_due = self.next_service_due_date
            self.vehicle.odometer_reading = self.odometer_reading
            self.vehicle.save(update_fields=['last_service_date', 'next_service_due', 'odometer_reading'])


class VehicleAssignmentHistory(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )
    trainer = models.ForeignKey(
        Trainer, 
        on_delete=models.CASCADE,
        related_name='vehicle_history'
    )
    
    assigned_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)

    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('vehicle', 'assigned_date')  # Prevent duplicate assignments on the same date
    
    def __str__(self):
        status = "Active" if not self.returned_date else "Returned"
        return f"{self.vehicle} assigned to {self.trainer} ({status})"

    def save(self, *args, **kwargs):
        """Ensure a vehicle is not assigned to multiple trainers at the same time"""
        if not self.returned_date:
            existing_assignment = VehicleAssignmentHistory.objects.filter(
                vehicle=self.vehicle, 
                returned_date__isnull=True
            ).exclude(id=self.id)
            
            if existing_assignment.exists():
                raise ValueError("This vehicle is already assigned to another trainer.")
        
        super().save(*args, **kwargs)