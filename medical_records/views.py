from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import MedicalRecord
from .forms import MedicalRecordForm
from patients.models import Patient

def has_upload_permission(user):
    return hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'DOCTOR', 'RECEPTIONIST']

# List records for a patient (for doctor/admin/receptionist)
@login_required
def patient_records(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    # Permission: only admin, doctor, receptionist can see all records; patient can only see their own
    if hasattr(request.user, 'profile'):
        role = request.user.profile.role
        if role == 'PATIENT':
            # Allow only if the patient is the logged-in user
            if request.user != patient.user:
                messages.error(request, 'You do not have permission to view these records.')
                return redirect('accounts:patient_dashboard')
        elif role not in ['ADMIN', 'DOCTOR', 'RECEPTIONIST']:
            messages.error(request, 'You do not have permission to view these records.')
            return redirect('accounts:patient_dashboard')
    else:
        messages.error(request, 'Permission denied.')
        return redirect('accounts:login')

    records = MedicalRecord.objects.filter(patient=patient).order_by('-upload_date')
    context = {
        'patient': patient,
        'records': records,
    }
    return render(request, 'medical_records/patient_records.html', context)

# Upload record (admin/doctor/receptionist)
@login_required
def upload_record(request):
    if not has_upload_permission(request.user):
        messages.error(request, 'You do not have permission to upload records.')
        return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.uploaded_by = request.user
            record.save()
            messages.success(request, f'Record "{record.title}" uploaded successfully.')
            return redirect('medical_records:patient_records', patient_id=record.patient.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MedicalRecordForm()

    return render(request, 'medical_records/upload_record.html', {'form': form})

# Delete record (admin/doctor/receptionist)
@login_required
def delete_record(request, pk):
    if not has_upload_permission(request.user):
        messages.error(request, 'You do not have permission to delete records.')
        return redirect('accounts:patient_dashboard')

    record = get_object_or_404(MedicalRecord, pk=pk)
    patient_id = record.patient.id
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Record deleted successfully.')
        return redirect('medical_records:patient_records', patient_id=patient_id)

    return render(request, 'medical_records/delete_confirm.html', {'record': record})