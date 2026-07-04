from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Appointment
from .forms import AppointmentForm

# ----- Helper: Check if user is Admin OR Receptionist -----
def has_booking_permission(user):
    """Return True if user is Admin or Receptionist."""
    return hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'RECEPTIONIST']

def has_status_permission(user):
    """Return True if user is Admin, Receptionist, or Doctor."""
    return hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'RECEPTIONIST', 'DOCTOR']


# 1. List Appointments
@login_required
def appointment_list(request):
    if not has_booking_permission(request.user):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:patient_dashboard')

    query = request.GET.get('q', '')
    appointments = Appointment.objects.all().select_related('patient', 'doctor')

    if query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(doctor__first_name__icontains=query) |
            Q(doctor__last_name__icontains=query) |
            Q(status__icontains=query)
        )

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    paginator = Paginator(appointments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return render(request, 'appointments/appointment_list.html', context)


# 2. Add Appointment
@login_required
def appointment_add(request):
    if not has_booking_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f'Appointment #{appointment.appointment_id} booked successfully!')
            return redirect('appointments:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Book Appointment'})


# 3. Edit Appointment
@login_required
def appointment_edit(request, pk):
    if not has_booking_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Appointment #{appointment.appointment_id} updated successfully!')
            return redirect('appointments:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/appointment_form.html', {'form': form, 'title': 'Edit Appointment', 'appointment': appointment})


# 4. Delete Appointment
@login_required
def appointment_delete(request, pk):
    if not has_booking_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment_id = appointment.appointment_id
        appointment.delete()
        messages.success(request, f'Appointment #{appointment_id} deleted successfully!')
        return redirect('appointments:list')

    return render(request, 'appointments/appointment_confirm_delete.html', {'appointment': appointment})


# 5. Update Status (Quick Action) - Updated for Doctors
@login_required
def appointment_update_status(request, pk, status):
    if not has_status_permission(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    appointment = get_object_or_404(Appointment, pk=pk)
    
    # If user is a DOCTOR, only allow updating their OWN appointments
    if hasattr(request.user, 'profile') and request.user.profile.role == 'DOCTOR':
        try:
            doctor = request.user.doctor_profile
            if appointment.doctor != doctor:
                messages.error(request, 'You can only update status for your own appointments.')
                return redirect('accounts:doctor_dashboard')
        except:
            messages.error(request, 'Doctor profile not found.')
            return redirect('accounts:doctor_dashboard')

    # Check if status is valid
    if status not in dict(Appointment.STATUS_CHOICES):
        messages.error(request, 'Invalid status.')
        return redirect('appointments:list')

    # Prevent changing status if already completed or cancelled
    if appointment.status == 'Completed':
        messages.warning(request, f'Appointment #{appointment.appointment_id} is already completed.')
        return redirect('appointments:list')
    
    if appointment.status == 'Cancelled':
        messages.warning(request, f'Appointment #{appointment.appointment_id} is cancelled.')
        return redirect('appointments:list')

    # Update status
    appointment.status = status
    appointment.save()
    messages.success(request, f'Appointment #{appointment.appointment_id} status updated to "{status}".')
    
    # Redirect based on role
    if hasattr(request.user, 'profile') and request.user.profile.role == 'DOCTOR':
        return redirect('accounts:doctor_dashboard')
    else:
        return redirect('appointments:list')