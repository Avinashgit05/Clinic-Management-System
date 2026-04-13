from django.contrib import admin
from tokens.models import TokenQueue


@admin.register(TokenQueue)
class TokenQueueAdmin(admin.ModelAdmin):
    list_display = ['token_number', 'appointment', 'status', 'called_at', 'completed_at', 'created_at']
    list_filter = ['status', 'appointment__date']
    search_fields = ['appointment__patient__user__first_name', 'appointment__doctor__user__first_name']
    ordering = ['appointment__date', 'token_number']
