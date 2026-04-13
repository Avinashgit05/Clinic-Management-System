from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from patients.models import PatientProfile
from patients.forms import PatientProfileForm
from appointments.models import Appointment, TIME_SLOT_CHOICES
from appointments.forms import AppointmentBookingForm, RescheduleForm
from tokens.models import TokenQueue
from doctors.models import DoctorProfile


def patient_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_patient:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access denied.")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


@patient_required
def dashboard(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    today = timezone.now().date()
    upcoming = Appointment.objects.filter(
        patient=profile, date__gte=today,
        status__in=['confirmed', 'pending']
    ).select_related('doctor__user')[:5]
    recent = Appointment.objects.filter(
        patient=profile
    ).select_related('doctor__user').order_by('-date')[:5]
    total_appointments = Appointment.objects.filter(patient=profile).count()
    completed = Appointment.objects.filter(patient=profile, status='completed').count()

    # Today's active token
    today_token = None
    today_appt = Appointment.objects.filter(
        patient=profile, date=today,
        status__in=['confirmed', 'pending']
    ).first()
    if today_appt:
        try:
            today_token = today_appt.token
        except TokenQueue.DoesNotExist:
            pass

    context = {
        'profile': profile,
        'upcoming': upcoming,
        'recent': recent,
        'total_appointments': total_appointments,
        'completed': completed,
        'today_token': today_token,
    }
    return render(request, 'patients/dashboard.html', context)


@patient_required
def profile_view(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    form = PatientProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('patients:profile')
    return render(request, 'patients/profile.html', {'form': form, 'profile': profile})


@patient_required
def book_appointment(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    form = AppointmentBookingForm(request.POST or None)
    booked_slots = []

    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = profile
        appointment.status = 'confirmed'
        appointment.save()
        # Auto-generate token
        token_num = TokenQueue.generate_token_number(appointment.doctor, appointment.date)
        TokenQueue.objects.create(appointment=appointment, token_number=token_num)
        messages.success(
            request,
            f"✅ Appointment booked! Your token number is #{token_num}. "
            f"[MOCK SMS] Confirmation sent to your registered contact."
        )
        return redirect('patients:my_appointments')

    # For AJAX: get booked slots for selected doctor + date
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if doctor_id and date_str:
        try:
            from datetime import date as date_type
            import datetime
            d = datetime.date.fromisoformat(date_str)
            doctor = DoctorProfile.objects.get(pk=doctor_id)
            booked_slots = list(Appointment.get_booked_slots(doctor, d))
        except Exception:
            pass

    return render(request, 'patients/book_appointment.html', {
        'form': form,
        'all_slots': TIME_SLOT_CHOICES,
        'booked_slots': booked_slots,
    })


@patient_required
def my_appointments(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    appointments = Appointment.objects.filter(
        patient=profile
    ).select_related('doctor__user').order_by('-date', '-time_slot')
    return render(request, 'patients/my_appointments.html', {
        'appointments': appointments
    })


@patient_required
def cancel_appointment(request, pk):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, patient=profile)
    if appt.status in ['confirmed', 'pending']:
        appt.status = 'cancelled'
        appt.save()
        if hasattr(appt, 'token'):
            appt.token.status = 'skipped'
            appt.token.save()
        messages.warning(request, "Appointment cancelled. [MOCK SMS] Cancellation notice sent.")
    else:
        messages.error(request, "This appointment cannot be cancelled.")
    return redirect('patients:my_appointments')


@patient_required
def reschedule_appointment(request, pk):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, patient=profile)
    if appt.status not in ['confirmed', 'pending']:
        messages.error(request, "Only active appointments can be rescheduled.")
        return redirect('patients:my_appointments')
    form = RescheduleForm(request.POST or None, instance=appt)
    if request.method == 'POST' and form.is_valid():
        old_date = appt.date
        old_doctor = appt.doctor
        appt = form.save()
        # Regenerate token if date changed
        if hasattr(appt, 'token'):
            appt.token.token_number = TokenQueue.generate_token_number(appt.doctor, appt.date)
            appt.token.status = 'waiting'
            appt.token.save()
        messages.success(request, "Appointment rescheduled! [MOCK SMS] Update sent.")
        return redirect('patients:my_appointments')
    return render(request, 'patients/reschedule.html', {'form': form, 'appointment': appt})


@patient_required
def view_token(request, pk):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, patient=profile)
    token = get_object_or_404(TokenQueue, appointment=appt)
    current_token = TokenQueue.get_current_token(appt.doctor, appt.date)
    return render(request, 'patients/token_display.html', {
        'token': token,
        'appointment': appt,
        'current_token': current_token,
    })
