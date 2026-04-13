from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from accounts.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile
from doctors.forms import AddDoctorForm
from appointments.models import Appointment


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or (
            not request.user.is_superuser and not request.user.is_admin_user
        ):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Admin access required.")
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)


@admin_required
def dashboard(request):
    today = timezone.now().date()
    total_patients = PatientProfile.objects.count()
    total_doctors = DoctorProfile.objects.count()
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(date=today).count()
    pending = Appointment.objects.filter(status__in=['confirmed', 'pending']).count()
    completed = Appointment.objects.filter(status='completed').count()
    cancelled = Appointment.objects.filter(status='cancelled').count()
    recent_appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    ).order_by('-created_at')[:8]
    doctor_stats = DoctorProfile.objects.annotate(
        appt_count=Count('appointments')
    ).order_by('-appt_count')[:5]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending': pending,
        'completed': completed,
        'cancelled': cancelled,
        'recent_appointments': recent_appointments,
        'doctor_stats': doctor_stats,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def manage_doctors(request):
    form = AddDoctorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Doctor added successfully!")
        return redirect('admin_panel:doctors')
    doctors = DoctorProfile.objects.select_related('user').annotate(
        appt_count=Count('appointments')
    )
    return render(request, 'admin_panel/doctors.html', {'form': form, 'doctors': doctors})


@admin_required
def toggle_doctor(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    doctor.is_available = not doctor.is_available
    doctor.save()
    status = "enabled" if doctor.is_available else "disabled"
    messages.success(request, f"Dr. {doctor.user.get_full_name()} has been {status}.")
    return redirect('admin_panel:doctors')


@admin_required
def manage_patients(request):
    search = request.GET.get('q', '')
    patients = PatientProfile.objects.select_related('user').annotate(
        appt_count=Count('appointments')
    ).order_by('-created_at')
    if search:
        patients = patients.filter(
            user__first_name__icontains=search
        ) | patients.filter(
            user__last_name__icontains=search
        ) | patients.filter(
            user__username__icontains=search
        )
    return render(request, 'admin_panel/patients.html', {
        'patients': patients, 'search': search
    })


@admin_required
def all_appointments(request):
    date_filter = request.GET.get('date', '')
    doctor_filter = request.GET.get('doctor', '')
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    ).order_by('-date', 'time_slot')
    if date_filter:
        appointments = appointments.filter(date=date_filter)
    if doctor_filter:
        appointments = appointments.filter(doctor__pk=doctor_filter)
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    doctors = DoctorProfile.objects.select_related('user')
    return render(request, 'admin_panel/appointments.html', {
        'appointments': appointments,
        'doctors': doctors,
        'date_filter': date_filter,
        'doctor_filter': doctor_filter,
        'status_filter': status_filter,
    })


@admin_required
def reports(request):
    today = timezone.now().date()
    date_str = request.GET.get('date', today.isoformat())
    try:
        from datetime import date as dt
        import datetime
        report_date = datetime.date.fromisoformat(date_str)
    except Exception:
        report_date = today

    daily = Appointment.objects.filter(date=report_date).select_related(
        'patient__user', 'doctor__user'
    )
    doctor_report = DoctorProfile.objects.annotate(
        total=Count('appointments'),
        today_count=Count('appointments', filter=__import__('django.db.models', fromlist=['Q']).Q(
            appointments__date=report_date
        ))
    ).select_related('user')

    context = {
        'report_date': report_date,
        'daily_appointments': daily,
        'doctor_report': doctor_report,
        'daily_count': daily.count(),
        'daily_completed': daily.filter(status='completed').count(),
        'daily_cancelled': daily.filter(status='cancelled').count(),
    }
    return render(request, 'admin_panel/reports.html', context)
