from django.db import models
from django.contrib.auth.models import User
from departments.models import Department

class Doctor(models.Model):
    # Explicit primary key as per spec
    doctor_id = models.AutoField(primary_key=True)
    # One-to-One link to Django's built-in User for authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    specialization = models.CharField(max_length=100)
    experience = models.IntegerField()  # years of experience
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='doctors')
    profile_image = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialization})"

    class Meta:
        ordering = ['-joining_date']