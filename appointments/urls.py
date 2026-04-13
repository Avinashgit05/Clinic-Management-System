from django.urls import path
from appointments import views

app_name = 'appointments'

urlpatterns = [
    path('booked-slots/', views.get_booked_slots, name='booked_slots'),
]
