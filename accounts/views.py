from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from doctors.models import Doctor
from patients.models import Patient
from departments.models import Department
from appointments.models import Appointment
from django.db.models import Count, Q
from datetime import date
from django.views.decorators.csrf import csrf_exempt

def get_dashboard_url(user):
    """Return the URL name for the user's dashboard based on their role."""
    if hasattr(user, 'profile'):
        role = user.profile.role
        if role == 'ADMIN':
            return 'accounts:admin_dashboard'
        elif role == 'DOCTOR':
            return 'accounts:doctor_dashboard'
        elif role == 'RECEPTIONIST':
            return 'accounts:receptionist_dashboard'
        else:
            return 'accounts:patient_dashboard'
    # Fallback (e.g., for superusers without a profile)
    return 'accounts:admin_dashboard'

@csrf_exempt
def register(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(get_dashboard_url(user))
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

# Placeholder Dashboards
@login_required
def admin_dashboard(request):
    # Get counts for statistics
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_departments = Department.objects.count()
    total_appointments = Appointment.objects.count()
    
    # Today's appointments
    today = date.today()
    today_appointments = Appointment.objects.filter(appointment_date=today)
    today_scheduled = today_appointments.filter(status='Scheduled').count()
    today_completed = today_appointments.filter(status='Completed').count()
    today_cancelled = today_appointments.filter(status='Cancelled').count()
    
    # Recent appointments (last 10)
    recent_appointments = Appointment.objects.all().select_related('patient', 'doctor').order_by('-appointment_date', '-appointment_time')[:10]
    
    # Department-wise doctor count (for a small chart/donut later)
    departments_with_counts = Department.objects.annotate(
        doctor_count=Count('doctors')
    ).values('department_name', 'doctor_count')
    
    context = {
        'role': 'Admin',
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_departments': total_departments,
        'total_appointments': total_appointments,
        'today_scheduled': today_scheduled,
        'today_completed': today_completed,
        'today_cancelled': today_cancelled,
        'today_appointments_total': today_appointments.count(),
        'recent_appointments': recent_appointments,
        'departments_with_counts': departments_with_counts,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    return render(request, 'dashboards/doctor_dashboard.html', {'role': 'Doctor'})

@login_required
def receptionist_dashboard(request):
    return render(request, 'dashboards/receptionist_dashboard.html', {'role': 'Receptionist'})

@login_required
def patient_dashboard(request):
    return render(request, 'dashboards/patient_dashboard.html', {'role': 'Patient'})