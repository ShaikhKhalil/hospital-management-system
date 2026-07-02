from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'first_name', 'last_name', 'specialization', 'department', 'joining_date')
    list_filter = ('department', 'specialization')
    search_fields = ('first_name', 'last_name', 'email')
    raw_id_fields = ('user',)  # easier to select a user