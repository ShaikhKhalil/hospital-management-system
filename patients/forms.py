from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'user', 'first_name', 'last_name', 'gender', 'age', 
            'blood_group', 'email', 'phone', 'address', 'profile_image'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 2}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'User Account (login)',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'gender': 'Gender',
            'age': 'Age',
            'blood_group': 'Blood Group',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
            'profile_image': 'Profile Image',
        }