from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:login'), name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('doctors/', include('doctors.urls', namespace='doctors')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('tokens/', include('tokens.urls', namespace='tokens')),
    path('admin-panel/', include('patients.admin_urls', namespace='admin_panel')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
