from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'first_name', 'last_name', 'gender', 'age', 'blood_group', 'created_at')
    list_filter = ('gender', 'blood_group')
    search_fields = ('first_name', 'last_name', 'email')
    raw_id_fields = ('user',)