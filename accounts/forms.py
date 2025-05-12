# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
import re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
        error_messages={'invalid': 'Enter a valid email address'}
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
        error_messages={'required': 'First name is required'}
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
        error_messages={'required': 'Last name is required'}
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
        error_messages={'required': 'Phone number is required'}
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your address'}),
        required=True,
        error_messages={'required': 'Address is required'}
    )
    
    STUDENT_TYPE_CHOICES = (
        ('local', 'Local Student'),
        ('remote', 'Remote Student'),
    )
    student_type = forms.ChoiceField(
        choices=STUDENT_TYPE_CHOICES, 
        required=True,
        error_messages={'required': 'Please select a student type'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_username(self):
        """Validate that the username is alphanumeric and unique."""
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Username should only contain letters, numbers, and underscores.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Choose another one.")
        return username

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        """Validate phone number format."""
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?\d{10}$', phone_number):
            raise forms.ValidationError("Enter a valid phone number (10 digits).")
        return phone_number

    def clean(self):
        """Check if passwords match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Save the profile data
            user_profile = user.profile
            user_profile.phone_number = self.cleaned_data['phone_number']
            user_profile.address = self.cleaned_data['address']
            user_profile.student_type = self.cleaned_data['student_type']
            user_profile.user_type = 'student'  # Default user type is student
            user_profile.save()
        
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'student_type', 'profile_picture')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        if len(phone_number) < 10 :
            raise forms.ValidationError("Phone number should contain 10 digits.")
        return phone_number

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if len(address) < 10:
            raise forms.ValidationError("Address must be at least 10 characters long.")
        return address

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            file_size = profile_picture.size
            file_extension = profile_picture.name.split('.')[-1].lower()

            allowed_extensions = ['jpg', 'jpeg', 'png']
            max_size = 2 * 1024 * 1024  # 2MB

            if file_extension not in allowed_extensions:
                raise forms.ValidationError("Only JPG, JPEG, and PNG files are allowed.")
            if file_size > max_size:
                raise forms.ValidationError("Profile picture size should not exceed 2MB.")

        return profile_picture
  
        

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})