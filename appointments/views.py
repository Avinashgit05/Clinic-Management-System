from django.http import JsonResponse
from appointments.models import Appointment
from doctors.models import DoctorProfile
import datetime


def get_booked_slots(request):
    """Return booked slots for doctor+date as JSON (used by booking form AJAX)."""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if not doctor_id or not date_str:
        return JsonResponse({'booked': []})
    try:
        doctor = DoctorProfile.objects.get(pk=doctor_id)
        d = datetime.date.fromisoformat(date_str)
        booked = list(Appointment.get_booked_slots(doctor, d))
        return JsonResponse({'booked': booked})
    except Exception as e:
        return JsonResponse({'booked': [], 'error': str(e)})
