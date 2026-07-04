from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Prescription
from .forms import PrescriptionForm
from appointments.models import Appointment


# ----- Helpers -----
def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'

def is_doctor(user):
    return hasattr(user, 'profile') and user.profile.role == 'DOCTOR'

def has_prescription_permission(user):
    """Allow ADMIN, DOCTOR, and RECEPTIONIST to manage prescriptions."""
    return hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'DOCTOR', 'RECEPTIONIST']


# 1. List Prescriptions
@login_required
def prescription_list(request):
    if not has_prescription_permission(request.user):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:patient_dashboard')

    query = request.GET.get('q', '')
    prescriptions = Prescription.objects.all().select_related('appointment__patient', 'appointment__doctor')

    if query:
        prescriptions = prescriptions.filter(
            Q(appointment__patient__first_name__icontains=query) |
            Q(appointment__patient__last_name__icontains=query) |
            Q(appointment__doctor__first_name__icontains=query) |
            Q(appointment__doctor__last_name__icontains=query) |
            Q(diagnosis__icontains=query)
        )

    paginator = Paginator(prescriptions, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'query': query}
    return render(request, 'prescriptions/prescription_list.html', context)


# 2. Add Prescription
@login_required
def prescription_add(request):
    if not has_prescription_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    # Pre-fill appointment if provided in GET parameter
    initial_appointment = None
    appointment_id = request.GET.get('appointment')
    if appointment_id:
        try:
            initial_appointment = Appointment.objects.get(pk=appointment_id)
            # If user is a doctor, only allow prescribing for their own appointments
            if is_doctor(request.user):
                doctor = request.user.doctor_profile  # Get the doctor profile
                if initial_appointment.doctor != doctor:
                    messages.error(request, 'You can only prescribe for your own appointments.')
                    return redirect('accounts:doctor_dashboard')
        except Appointment.DoesNotExist:
            pass

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save()
            messages.success(request, f'Prescription created for Appointment #{prescription.appointment.appointment_id}')
            return redirect('prescriptions:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # If we have an initial appointment, pre-fill the form
        form = PrescriptionForm(initial={'appointment': initial_appointment})

    return render(request, 'prescriptions/prescription_form.html', {'form': form, 'title': 'Add Prescription'})


# 3. Edit Prescription
@login_required
def prescription_edit(request, pk):
    if not has_prescription_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    prescription = get_object_or_404(Prescription, pk=pk)
    
    # If user is a doctor, only allow editing their own prescriptions
    if is_doctor(request.user):
        doctor = request.user.doctor_profile
        if prescription.appointment.doctor != doctor:
            messages.error(request, 'You can only edit your own prescriptions.')
            return redirect('accounts:doctor_dashboard')

    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            form.save()
            messages.success(request, f'Prescription #{prescription.prescription_id} updated successfully!')
            return redirect('prescriptions:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PrescriptionForm(instance=prescription)

    return render(request, 'prescriptions/prescription_form.html', {'form': form, 'title': 'Edit Prescription', 'prescription': prescription})


# 4. Delete Prescription
@login_required
def prescription_delete(request, pk):
    if not has_prescription_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    prescription = get_object_or_404(Prescription, pk=pk)
    
    # Only ADMIN can delete prescriptions
    if not is_admin(request.user):
        messages.error(request, 'Only administrators can delete prescriptions.')
        return redirect('prescriptions:list')

    if request.method == 'POST':
        prescription_id = prescription.prescription_id
        prescription.delete()
        messages.success(request, f'Prescription #{prescription_id} deleted successfully!')
        return redirect('prescriptions:list')

    return render(request, 'prescriptions/prescription_confirm_delete.html', {'prescription': prescription})