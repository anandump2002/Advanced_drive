from django import forms
from django.utils import timezone
from .models import Vehicle, MaintenanceRecord
from trainers.models import Trainer

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_number', 'make', 'model', 'vehicle_type', 'purchased_year',
            'registration_expiry', 'insurance_expiry', 'seating_capacity',
            'is_active'  # ✅ Removed 'currently_assigned'
        ]
        widgets = {
            'registration_expiry': forms.DateInput(attrs={'type': 'date'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date'})
        }

class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            'maintenance_date', 'maintenance_type', 'description',
            'cost', 'odometer_reading', 'performed_by',
            'next_service_due_date', 'next_service_due_km', 'notes'
        ]
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'next_service_due_date': forms.DateInput(attrs={'type': 'date'})
        }

class VehicleAssignmentForm(forms.Form):
    trainer = forms.ModelChoiceField(
        queryset=Trainer.objects.filter(is_active=True),
        label="Assign to Trainer"
    )
    assigned_date = forms.DateField(
        initial=timezone.now().date(),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    reason = forms.CharField(
        widget=forms.Textarea,
        required=False
    )