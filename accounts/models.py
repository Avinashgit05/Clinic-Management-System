from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role()})"

    def get_role(self):
        if self.is_superuser or self.is_admin_user:
            return 'Admin'
        if self.is_doctor:
            return 'Doctor'
        if self.is_patient:
            return 'Patient'
        return 'Unknown'
