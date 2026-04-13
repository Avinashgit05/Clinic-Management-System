from django.contrib import admin
from patients.models import PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'contact_number', 'blood_group', 'age', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'contact_number']
    list_filter = ['gender', 'blood_group']
    readonly_fields = ['created_at', 'updated_at']
