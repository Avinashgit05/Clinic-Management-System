from django.contrib import admin
from doctors.models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'experience_years', 'consultation_fee', 'is_available', 'created_at']
    list_filter = ['specialization', 'is_available']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'specialization']
    list_editable = ['is_available']
