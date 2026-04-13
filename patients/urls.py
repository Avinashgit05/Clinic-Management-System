from django.urls import path
from patients import views

app_name = 'patients'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:pk>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('appointments/<int:pk>/token/', views.view_token, name='view_token'),
]
