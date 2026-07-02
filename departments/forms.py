from django import forms
from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'description']
        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter department name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Brief description', 'rows': 3}),
        }
        labels = {
            'department_name': 'Department Name',
            'description': 'Description',
        }