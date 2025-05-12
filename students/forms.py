from django import forms
from .models import Student, TrainingSession

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['address', 'phone_number', 'emergency_contact', 'student_type']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class SessionBookingForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ['trainer', 'vehicle', 'session_date', 'time_slot']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
        }


from django import forms
from .models import Payment, TrainingPackage

class PaymentForm(forms.ModelForm):
    package = forms.ModelChoiceField(
        queryset=TrainingPackage.objects.all(),
        empty_label="Select a Training Package",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Payment
        fields = ['package']


from django import forms
from .models import TrainingSession,Review
from django.utils import timezone
from datetime import date
from datetime import timedelta


class SlotBookingForm(forms.Form):
    session_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'min': date.today().isoformat()}
        ),
        label="Choose Date"
    )
    time_slot = forms.ChoiceField(
        choices=TrainingSession.TIME_SLOTS,
        label="Choose Time Slot"
    )

    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)  # Capture student instance
        super().__init__(*args, **kwargs)

    def clean_session_date(self):
        session_date = self.cleaned_data.get('session_date')
        min_date = timezone.now().date() + timedelta(days=1)  # Ensure booking is at least a day in advance

        if session_date and session_date < min_date:
            raise forms.ValidationError("You must book at least one day in advance. Booking for today is not allowed.")

        return session_date

    def clean(self):
        cleaned_data = super().clean()
        session_date = cleaned_data.get('session_date')
        time_slot = cleaned_data.get('time_slot')

        if self.student and session_date and time_slot:
            exists = TrainingSession.objects.filter(
                student=self.student,
                session_date=session_date,
                time_slot=time_slot
            ).exists()
            if exists:
                raise forms.ValidationError("You have already booked this time slot.")

        return cleaned_data



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }