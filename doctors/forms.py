from django import forms
from doctors.models import DoctorProfile
from accounts.models import User


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = [
            'specialization', 'contact_number', 'qualification',
            'experience_years', 'consultation_fee', 'bio', 'is_available'
        ]
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Contact number'
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. MBBS, MD, MS'
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0
            }),
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': 0
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Brief introduction about yourself'
            }),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AddDoctorForm(forms.ModelForm):
    """Admin form to create a new Doctor user."""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Initial Password'})
    )
    specialization = forms.ChoiceField(
        choices=DoctorProfile.specialization.field.choices if hasattr(DoctorProfile.specialization, 'field') else [],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number'})
    )
    qualification = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD'})
    )
    experience_years = forms.IntegerField(
        initial=0, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    consultation_fee = forms.DecimalField(
        initial=0.00, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_doctor = True
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                contact_number=self.cleaned_data.get('contact_number', ''),
                qualification=self.cleaned_data.get('qualification', ''),
                experience_years=self.cleaned_data.get('experience_years', 0),
                consultation_fee=self.cleaned_data.get('consultation_fee', 0.00),
            )
        return user
