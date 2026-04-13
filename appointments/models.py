from django.db import models
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from django.utils import timezone


def generate_time_slots():
    """Generate 30-minute slots from 9:00 AM to 5:00 PM."""
    slots = []
    from datetime import time
    hour = 9
    minute = 0
    while hour < 17:
        t = time(hour, minute)
        display = t.strftime('%I:%M %p')
        value = t.strftime('%H:%M')
        slots.append((value, display))
        minute += 30
        if minute == 60:
            minute = 0
            hour += 1
    return slots


TIME_SLOT_CHOICES = generate_time_slots()

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('no_show', 'No Show'),
]


class Appointment(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    reason = models.TextField(blank=True, help_text='Reason for visit')
    notes = models.TextField(blank=True, help_text='Doctor notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'date', 'time_slot')
        ordering = ['date', 'time_slot']

    def __str__(self):
        return (f"Appt #{self.pk} | "
                f"{self.patient.user.get_full_name()} → "
                f"Dr. {self.doctor.user.get_full_name()} | "
                f"{self.date} {self.time_slot}")

    def get_time_slot_display_label(self):
        for value, label in TIME_SLOT_CHOICES:
            if value == self.time_slot:
                return label
        return self.time_slot

    @staticmethod
    def get_booked_slots(doctor, date):
        return Appointment.objects.filter(
            doctor=doctor,
            date=date,
            status__in=['confirmed', 'pending']
        ).values_list('time_slot', flat=True)
