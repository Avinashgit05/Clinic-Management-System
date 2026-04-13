from django.urls import path
from patients import admin_views

app_name = 'admin_panel'

urlpatterns = [
    path('', admin_views.dashboard, name='dashboard'),
    path('doctors/', admin_views.manage_doctors, name='doctors'),
    path('doctors/<int:pk>/toggle/', admin_views.toggle_doctor, name='toggle_doctor'),
    path('patients/', admin_views.manage_patients, name='patients'),
    path('appointments/', admin_views.all_appointments, name='appointments'),
    path('reports/', admin_views.reports, name='reports'),
]
