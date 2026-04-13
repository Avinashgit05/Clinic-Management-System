from django.http import JsonResponse
from django.utils import timezone
from tokens.models import TokenQueue
from doctors.models import DoctorProfile
from django.contrib.auth.decorators import login_required


@login_required
def token_status_api(request, doctor_id):
    """AJAX endpoint — returns current & next token for a doctor today."""
    try:
        doctor = DoctorProfile.objects.get(pk=doctor_id)
    except DoctorProfile.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)

    today = timezone.now().date()
    current = TokenQueue.get_current_token(doctor, today)
    next_t = TokenQueue.get_next_waiting(doctor, today)

    # Patient's own token position
    my_token_num = None
    if request.user.is_patient:
        try:
            from appointments.models import Appointment
            appt = Appointment.objects.get(
                patient=request.user.patient_profile,
                doctor=doctor,
                date=today,
                status__in=['confirmed', 'pending']
            )
            my_token_num = appt.token.token_number
        except Exception:
            pass

    waiting_count = TokenQueue.objects.filter(
        appointment__doctor=doctor,
        appointment__date=today,
        status='waiting'
    ).count()

    data = {
        'current_token': current.token_number if current else None,
        'current_patient': current.appointment.patient.user.get_full_name() if current else None,
        'next_token': next_t.token_number if next_t else None,
        'waiting_count': waiting_count,
        'my_token': my_token_num,
    }
    return JsonResponse(data)
