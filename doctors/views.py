from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Doctor
from .forms import DoctorForm
from departments.models import Department
from django.contrib.auth.models import User

def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'

# 1. List Doctors
@login_required
def doctor_list(request):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:patient_dashboard')

    query = request.GET.get('q', '')
    doctors = Doctor.objects.all().select_related('department', 'user')

    if query:
        doctors = doctors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(department__department_name__icontains=query)
        )

    paginator = Paginator(doctors, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'doctors/doctor_list.html', context)

# 2. Add Doctor
@login_required
def doctor_add(request):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f'Dr. {doctor.first_name} {doctor.last_name} added successfully!')
            return redirect('doctors:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorForm()

    # Pre-fill the user field queryset to only show users who are not already doctors or patients?
    # But for simplicity, we show all users; you can later filter.
    context = {'form': form, 'title': 'Add Doctor'}
    return render(request, 'doctors/doctor_form.html', context)

# 3. Edit Doctor
@login_required
def doctor_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dr. {doctor.first_name} {doctor.last_name} updated successfully!')
            return redirect('doctors:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorForm(instance=doctor)

    context = {'form': form, 'title': 'Edit Doctor', 'doctor': doctor}
    return render(request, 'doctors/doctor_form.html', context)

# 4. Delete Doctor
@login_required
def doctor_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        full_name = f"{doctor.first_name} {doctor.last_name}"
        doctor.delete()
        messages.success(request, f'Dr. {full_name} deleted successfully!')
        return redirect('doctors:list')

    return render(request, 'doctors/doctor_confirm_delete.html', {'doctor': doctor})