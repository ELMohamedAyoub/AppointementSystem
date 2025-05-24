from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/accounts/', include('medicalpro.accounts.urls')),
    path('api/appointments/', include('medicalpro.appointments.urls')),
    path('api/doctors/', include('medicalpro.doctors.urls')),
    path('api/patients/', include('medicalpro.patients.urls')),
    path('api/prescriptions/', include('medicalpro.prescriptions.urls')),
    
    # React app will handle frontend routes
    path('', TemplateView.as_view(template_name='index.html')),
    # This route ensures React router handles client-side routing
    path('<path:path>', TemplateView.as_view(template_name='index.html')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 