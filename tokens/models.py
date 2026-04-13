from django.db import models
from appointments.models import Appointment


TOKEN_STATUS_CHOICES = [
    ('waiting', 'Waiting'),
    ('called', 'Called'),
    ('completed', 'Completed'),
    ('skipped', 'Skipped'),
]


class TokenQueue(models.Model):
    appointment = models.OneToOneField(
        Appointment, on_delete=models.CASCADE, related_name='token'
    )
    token_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=TOKEN_STATUS_CHOICES, default='waiting')
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['token_number']
        unique_together = ('appointment',)

    def __str__(self):
        return (f"Token #{self.token_number} | "
                f"{self.appointment.patient.user.get_full_name()} | "
                f"{self.status}")

    @staticmethod
    def generate_token_number(doctor, date):
        """Auto-increment per doctor per day."""
        existing = TokenQueue.objects.filter(
            appointment__doctor=doctor,
            appointment__date=date
        ).order_by('-token_number').first()
        return (existing.token_number + 1) if existing else 1

    @staticmethod
    def get_current_token(doctor, date):
        """Return the currently called token for a doctor today."""
        return TokenQueue.objects.filter(
            appointment__doctor=doctor,
            appointment__date=date,
            status='called'
        ).first()

    @staticmethod
    def get_next_waiting(doctor, date):
        """Return the next waiting token."""
        return TokenQueue.objects.filter(
            appointment__doctor=doctor,
            appointment__date=date,
            status='waiting'
        ).order_by('token_number').first()
