from django.contrib import admin
from appointments.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'date', 'time_slot', 'status', 'created_at']
    list_filter = ['status', 'date', 'doctor__specialization']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name']
    list_editable = ['status']
    date_hierarchy = 'date'
    ordering = ['-date', 'time_slot']
