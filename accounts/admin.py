from django.contrib import admin
from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'get_full_name', 'is_patient', 'is_doctor', 'is_admin_user', 'is_active']
    list_filter = ['is_patient', 'is_doctor', 'is_admin_user', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
