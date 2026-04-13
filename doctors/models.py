from django.db import models
from accounts.models import User


SPECIALIZATION_CHOICES = [
    ('General Physician', 'General Physician'),
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologist', 'Dermatologist'),
    ('Neurologist', 'Neurologist'),
    ('Orthopedic', 'Orthopedic'),
    ('Pediatrician', 'Pediatrician'),
    ('Psychiatrist', 'Psychiatrist'),
    ('ENT Specialist', 'ENT Specialist'),
    ('Gynecologist', 'Gynecologist'),
    ('Ophthalmologist', 'Ophthalmologist'),
    ('Dentist', 'Dentist'),
    ('Other', 'Other'),
]


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    contact_number = models.CharField(max_length=15, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization})"
