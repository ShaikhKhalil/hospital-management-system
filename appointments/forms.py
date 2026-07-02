from django import forms
from .models import Appointment
from datetime import date

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'remarks']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any special notes', 'rows': 2}),
        }
        labels = {
            'patient': 'Patient',
            'doctor': 'Doctor',
            'appointment_date': 'Appointment Date',
            'appointment_time': 'Appointment Time',
            'status': 'Status',
            'remarks': 'Remarks',
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        doctor = cleaned_data.get('doctor')

        # 1. Cannot book appointment in the past
        if appointment_date and appointment_date < date.today():
            raise forms.ValidationError("Cannot book an appointment in the past.")

        # 2. Check if doctor is already booked at that date/time
        # We exclude the current appointment if we're editing
        instance = getattr(self, 'instance', None)
        if doctor and appointment_date and appointment_time:
            existing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
            if instance and instance.pk:
                existing = existing.exclude(pk=instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    f"Dr. {doctor.first_name} {doctor.last_name} already has an appointment at this date and time."
                )

        return cleaned_data