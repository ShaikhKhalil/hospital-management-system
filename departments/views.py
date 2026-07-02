from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Department
from .forms import DepartmentForm

# Helper: Check if user is Admin
def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'

# 1. List Departments with Search & Pagination
@login_required
def department_list(request):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('accounts:patient_dashboard')  # fallback

    query = request.GET.get('q', '')
    departments = Department.objects.all()

    if query:
        departments = departments.filter(
            Q(department_name__icontains=query) |
            Q(description__icontains=query)
        )

    paginator = Paginator(departments, 5)  # Show 5 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'departments/department_list.html', context)

# 2. Add Department
@login_required
def department_add(request):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{form.cleaned_data["department_name"]}" added successfully!')
            return redirect('departments:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DepartmentForm()

    return render(request, 'departments/department_form.html', {'form': form, 'title': 'Add Department'})

# 3. Edit Department
@login_required
def department_edit(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{form.cleaned_data["department_name"]}" updated successfully!')
            return redirect('departments:list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DepartmentForm(instance=department)

    return render(request, 'departments/department_form.html', {'form': form, 'title': 'Edit Department'})

# 4. Delete Department
@login_required
def department_delete(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('accounts:patient_dashboard')

    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department_name = department.department_name
        department.delete()
        messages.success(request, f'Department "{department_name}" deleted successfully!')
        return redirect('departments:list')

    return render(request, 'departments/department_confirm_delete.html', {'department': department})

def is_admin(user):
    print("User:", user.username)
    print("Has profile:", hasattr(user, 'profile'))
    if hasattr(user, 'profile'):
        print("Role:", user.profile.role)
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'