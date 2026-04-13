from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from doctors.models import DoctorProfile
from doctors.forms import DoctorProfileForm
from appointments.models import Appointment
from tokens.models import TokenQueue


def doctor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_doctor:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Access denied.")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


@doctor_required
def dashboard(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        doctor=doctor, date=today,
        status__in=['confirmed', 'pending', 'completed']
    ).select_related('patient__user').order_by('time_slot')
    pending_count = today_appointments.filter(status__in=['confirmed', 'pending']).count()
    completed_count = today_appointments.filter(status='completed').count()
    total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()

    current_token = TokenQueue.get_current_token(doctor, today)
    next_token = TokenQueue.get_next_waiting(doctor, today)
    queue = TokenQueue.objects.filter(
        appointment__doctor=doctor,
        appointment__date=today,
        status__in=['waiting', 'called']
    ).select_related('appointment__patient__user').order_by('token_number')

    context = {
        'doctor': doctor,
        'today': today,
        'today_appointments': today_appointments,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'total_patients': total_patients,
        'current_token': current_token,
        'next_token': next_token,
        'queue': queue,
    }
    return render(request, 'doctors/dashboard.html', context)


@doctor_required
def profile_view(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    form = DoctorProfileForm(request.POST or None, instance=doctor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('doctors:profile')
    return render(request, 'doctors/profile.html', {'form': form, 'doctor': doctor})


@doctor_required
def appointment_list(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    date_filter = request.GET.get('date', '')
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user').order_by('-date', 'time_slot')
    if date_filter:
        appointments = appointments.filter(date=date_filter)
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'doctors/appointments.html', {
        'appointments': appointments,
        'date_filter': date_filter,
        'status_filter': status_filter,
    })


@doctor_required
def mark_completed(request, pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    if request.method == 'POST':
        appt.status = 'completed'
        appt.notes = request.POST.get('notes', '')
        appt.save()
        if hasattr(appt, 'token'):
            appt.token.status = 'completed'
            appt.token.completed_at = timezone.now()
            appt.token.save()
        messages.success(request, f"Patient {appt.patient.user.get_full_name()} marked as completed.")
    return redirect('doctors:dashboard')


@doctor_required
def call_next_token(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    today = timezone.now().date()
    if request.method == 'POST':
        # Mark current 'called' token as completed first
        current = TokenQueue.get_current_token(doctor, today)
        if current:
            current.status = 'completed'
            current.completed_at = timezone.now()
            current.save()
            current.appointment.status = 'completed'
            current.appointment.save()
        # Get next waiting
        next_token = TokenQueue.get_next_waiting(doctor, today)
        if next_token:
            next_token.status = 'called'
            next_token.called_at = timezone.now()
            next_token.save()
            messages.success(request, f"Now serving Token #{next_token.token_number} — {next_token.appointment.patient.user.get_full_name()}")
        else:
            messages.info(request, "No more patients in the queue.")
    return redirect('doctors:dashboard')


@doctor_required
def patient_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    return render(request, 'doctors/patient_detail.html', {'appointment': appt})
