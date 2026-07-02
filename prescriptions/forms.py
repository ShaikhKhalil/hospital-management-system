from django import forms
from .models import Prescription
from appointments.models import Appointment

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['appointment', 'diagnosis', 'medicines', 'notes']
        widgets = {
            'appointment': forms.Select(attrs={'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter diagnosis', 'rows': 2}),
            'medicines': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'List medicines (comma separated)', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Additional notes', 'rows': 2}),
        }
        labels = {
            'appointment': 'Appointment',
            'diagnosis': 'Diagnosis',
            'medicines': 'Medicines',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit appointment choices to those WITHOUT a prescription
        # But only if we're adding (not editing)
        if not self.instance.pk:
            appointments_with_prescription = Prescription.objects.values_list('appointment_id', flat=True)
            self.fields['appointment'].queryset = Appointment.objects.exclude(
                appointment_id__in=appointments_with_prescription
            )