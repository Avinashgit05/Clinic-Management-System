from django.core.management.base import BaseCommand
from accounts.models import User
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from appointments.models import Appointment
from tokens.models import TokenQueue
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seed the database with sample Clinic data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@clinic.com', 'admin123')
            admin.first_name = 'Clinic'
            admin.last_name = 'Admin'
            admin.is_admin_user = True
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created Admin: admin/admin123"))

        # 2. Doctors
        docs = [
            {'u': 'dr_smith', 'f': 'John', 'l': 'Smith', 's': 'Cardiologist'},
            {'u': 'dr_jane', 'f': 'Jane', 'l': 'Doe', 's': 'General Physician'},
        ]
        for d in docs:
            if not User.objects.filter(username=d['u']).exists():
                u = User.objects.create_user(d['u'], f"{d['u']}@clinic.com", 'password123')
                u.first_name = d['f']
                u.last_name = d['l']
                u.is_doctor = True
                u.save()
                DoctorProfile.objects.create(
                    user=u, specialization=d['s'], experience_years=10, consultation_fee=150.00
                )
                self.stdout.write(self.style.SUCCESS(f"Created Doctor: {d['u']}/password123"))

        # 3. Patient
        if not User.objects.filter(username='patient1').exists():
            p = User.objects.create_user('patient1', 'patient1@clinic.com', 'password123')
            p.first_name = 'Sam'
            p.last_name = 'Patient'
            p.is_patient = True
            p.save()
            prof = PatientProfile.objects.create(user=p, contact_number='1234567890', blood_group='O+')
            self.stdout.write(self.style.SUCCESS("Created Patient: patient1/password123"))

            # Create an appointment for today
            try:
                doctor = DoctorProfile.objects.first()
                today = timezone.now().date()
                appt = Appointment.objects.create(
                    patient=prof,
                    doctor=doctor,
                    date=today,
                    time_slot='09:00',
                    status='pending',
                    reason='Routine checkup'
                )
                TokenQueue.objects.create(appointment=appt, token_number=1, status='waiting')
                self.stdout.write(self.style.SUCCESS("Booked sample appointment and token generated."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not create appointment: {e}"))
