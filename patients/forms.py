from django import forms
from patients.models import PatientProfile


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'date_of_birth', 'gender', 'contact_number',
            'address', 'blood_group', 'medical_history', 'emergency_contact'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. +91-9876543210'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Your address'
            }),
            'blood_group': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. A+, B-, O+'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Any chronic conditions, allergies, past surgeries...'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Emergency contact number'
            }),
        }
