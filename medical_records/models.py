from django.db import models
from patients.models import Patient
from django.contrib.auth.models import User
from django.utils import timezone

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='medical_records/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.title}"

    class Meta:
        ordering = ['-upload_date']