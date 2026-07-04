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
from prescriptions.models import Prescription

def get_dashboard_url(user):
    if hasattr(user, 'profile'):
        role = user.profile.role
        if role == 'ADMIN':
            return 'accounts:admin_dashboard'
        elif role == 'DOCTOR':
            return 'accounts:doctor_dashboard'
        elif role == 'RECEPTIONIST':
            return 'accounts:receptionist_dashboard'  # ✅ Must be this
        else:
            return 'accounts:patient_dashboard'
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
    # Get the doctor profile for this user
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        context = {
            'role': 'Doctor',
            'has_doctor_profile': False,
        }
        return render(request, 'dashboards/doctor_dashboard.html', context)

    today = date.today()

    # Today's appointments (Scheduled or Completed for today)
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).select_related('patient').order_by('appointment_time')

    # Upcoming appointments (future dates, Scheduled)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gt=today,
        status='Scheduled'
    ).select_related('patient').order_by('appointment_date', 'appointment_time')

    # Past appointments (for history)
    past_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__lt=today
    ).select_related('patient').order_by('-appointment_date')

    # Total patients the doctor has seen (distinct patients)
    total_patients_seen = Appointment.objects.filter(
        doctor=doctor,
        status='Completed'
    ).values('patient').distinct().count()

    # Today's stats
    today_scheduled = today_appointments.filter(status='Scheduled').count()
    today_completed = today_appointments.filter(status='Completed').count()
    today_cancelled = today_appointments.filter(status='Cancelled').count()

    # Prescriptions written by this doctor
    prescriptions_count = Prescription.objects.filter(
        appointment__doctor=doctor
    ).count()

    context = {
        'role': 'Doctor',
        'doctor': doctor,
        'has_doctor_profile': True,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments[:5],
        'past_appointments': past_appointments[:5],
        'total_patients_seen': total_patients_seen,
        'today_scheduled': today_scheduled,
        'today_completed': today_completed,
        'today_cancelled': today_cancelled,
        'prescriptions_count': prescriptions_count,
        'today': today,
    }
    return render(request, 'dashboards/doctor_dashboard.html', context)

@login_required
def receptionist_dashboard(request):
    # Get statistics for today
    today = date.today()
    today_appointments = Appointment.objects.filter(appointment_date=today)
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    recent_patients = Patient.objects.all().order_by('-created_at')[:5]
    recent_appointments = Appointment.objects.all().select_related('patient', 'doctor').order_by('-appointment_date', '-appointment_time')[:5]

    context = {
        'role': 'Receptionist',
        'today_appointments_count': today_appointments.count(),
        'today_scheduled': today_appointments.filter(status='Scheduled').count(),
        'today_completed': today_appointments.filter(status='Completed').count(),
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'dashboards/receptionist_dashboard.html', context)

@login_required
def patient_dashboard(request):
    # Only PATIENT role can access this dashboard
    if hasattr(request.user, 'profile') and request.user.profile.role != 'PATIENT':
        messages.error(request, 'You do not have permission to view this page.')
        return redirect(get_dashboard_url(request.user))

    # Get the patient profile for this user (if exists)
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        patient = None

    if not patient:
        context = {
            'role': 'Patient',
            'has_patient_profile': False,
        }
        return render(request, 'dashboards/patient_dashboard.html', context)

    today = date.today()

    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=today,
        status='Scheduled'
    ).select_related('doctor', 'patient').order_by('appointment_date', 'appointment_time')

    past_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__lt=today
    ).select_related('doctor', 'patient').order_by('-appointment_date', '-appointment_time')

    completed_count = Appointment.objects.filter(
        patient=patient,
        status='Completed'
    ).count()

    prescriptions = Prescription.objects.filter(
        appointment__patient=patient
    ).select_related('appointment__doctor', 'appointment').order_by('-created_at')

    context = {
        'role': 'Patient',
        'patient': patient,
        'has_patient_profile': True,
        'upcoming_appointments': upcoming_appointments[:5],
        'past_appointments': past_appointments[:10],
        'completed_count': completed_count,
        'prescriptions': prescriptions[:5],
        'today': today,
    }
    return render(request, 'dashboards/patient_dashboard.html', context)