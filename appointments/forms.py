from django import forms
from appointments.models import Appointment, TIME_SLOT_CHOICES
from doctors.models import DoctorProfile
from django.utils import timezone


class AppointmentBookingForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=DoctorProfile.objects.filter(is_available=True),
        empty_label='-- Select Doctor --',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control', 'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    time_slot = forms.ChoiceField(
        choices=[('', '-- Select Time Slot --')] + list(TIME_SLOT_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_time_slot'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'Describe your symptoms or reason for visit...'
        })
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time_slot', 'reason']

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and date and time_slot:
            if date < timezone.now().date():
                raise forms.ValidationError("Cannot book an appointment in the past.")
            if Appointment.objects.filter(
                doctor=doctor, date=date, time_slot=time_slot,
                status__in=['confirmed', 'pending']
            ).exists():
                raise forms.ValidationError(
                    f"This time slot is already booked. Please choose a different slot."
                )
        return cleaned_data


class RescheduleForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control', 'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    time_slot = forms.ChoiceField(
        choices=[('', '-- Select Time Slot --')] + list(TIME_SLOT_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['date', 'time_slot']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')
        if date and date < timezone.now().date():
            raise forms.ValidationError("Cannot reschedule to a past date.")
        if self.instance and date and time_slot:
            if Appointment.objects.filter(
                doctor=self.instance.doctor,
                date=date,
                time_slot=time_slot,
                status__in=['confirmed', 'pending']
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("That slot is already taken. Pick another.")
        return cleaned_data
