from django.urls import path
from tokens import views

app_name = 'tokens'

urlpatterns = [
    path('api/status/<int:doctor_id>/', views.token_status_api, name='status_api'),
]
