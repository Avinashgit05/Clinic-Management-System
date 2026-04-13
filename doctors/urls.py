from django.urls import path
from doctors import views

app_name = 'doctors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('appointments/', views.appointment_list, name='appointments'),
    path('appointments/<int:pk>/complete/', views.mark_completed, name='mark_completed'),
    path('appointments/<int:pk>/detail/', views.patient_detail, name='patient_detail'),
    path('queue/next/', views.call_next_token, name='call_next'),
]
