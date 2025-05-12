# admins/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Admin

class AdminRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea, required=False)
    is_primary = forms.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        
class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    

from vehicles.models import Vehicle, MaintenanceRecord, VehicleAssignmentHistory, Trainer


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_number', 'make', 'model', 'vehicle_type', 
            'purchased_year', 'registration_expiry', 'insurance_expiry',
            'seating_capacity', 'is_active'
        ]
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter vehicle number'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter make'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter model'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'purchased_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter purchased year'}),
            'registration_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'insurance_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter seating capacity'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
            'maintenance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter cost'}),
            'odometer_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter odometer reading'}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter performed by'}),
            'next_service_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_service_due_km': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter next service due km'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }

class VehicleAssignmentForm(forms.ModelForm):
    class Meta:
        model = VehicleAssignmentHistory
        fields = ['trainer', 'assigned_date', 'reason', 'notes']
        widgets = {
            'trainer': forms.Select(attrs={'class': 'form-select'}),
            'assigned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter reason'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }

class ReturnVehicleForm(forms.Form):
    returned_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        required=False
    )