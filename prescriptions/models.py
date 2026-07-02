from django.db import models
from appointments.models import Appointment

class Prescription(models.Model):
    prescription_id = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    diagnosis = models.TextField()
    medicines = models.TextField()  # can be a comma-separated list or detailed text
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment.patient} (Appt #{self.appointment.appointment_id})"