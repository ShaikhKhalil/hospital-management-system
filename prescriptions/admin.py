from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('prescription_id', 'appointment', 'diagnosis', 'created_at')
    search_fields = ('appointment__patient__first_name', 'appointment__patient__last_name')
    raw_id_fields = ('appointment',)