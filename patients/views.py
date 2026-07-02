from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Patient
from .forms import PatientForm

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'

# 1. List Patients
@login_required
def patient_list(request):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:patient_dashboard')

    query = request.GET.get('q', '')
    patients = Patient.objects.all().select_related('user')

    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    paginator = Paginator(patients, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'query': query}
    return render(request, 'patients/patient_list.html', context)

# 2. Add Patient
@login_required
def patient_add(request):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f'Patient {patient.first_name} {patient.last_name} added successfully!')
            return redirect('patients:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientForm()

    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Add Patient'})

# 3. Edit Patient
@login_required
def patient_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient {patient.first_name} {patient.last_name} updated successfully!')
            return redirect('patients:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Edit Patient', 'patient': patient})

# 4. Delete Patient
@login_required
def patient_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        full_name = f"{patient.first_name} {patient.last_name}"
        patient.delete()
        messages.success(request, f'Patient {full_name} deleted successfully!')
        return redirect('patients:list')

    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})