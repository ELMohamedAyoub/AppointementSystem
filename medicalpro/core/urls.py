from django.urls import path

from medicalpro.core import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # System settings
    path('settings/', views.SystemSettingListView.as_view(), name='system_settings'),
    path('settings/<str:key>/', views.SystemSettingDetailView.as_view(), name='system_setting_detail'),
    
    # Logs
    path('logs/api/', views.APILogListView.as_view(), name='api_logs'),
    path('logs/error/', views.ErrorLogListView.as_view(), name='error_logs'),
    path('logs/audit/', views.AuditLogListView.as_view(), name='audit_logs'),
    
    # Scheduled tasks
    path('tasks/', views.ScheduledTaskListView.as_view(), name='scheduled_tasks'),
    path('tasks/<int:pk>/', views.ScheduledTaskDetailView.as_view(), name='scheduled_task_detail'),
    path('tasks/create/', views.ScheduledTaskCreateView.as_view(), name='scheduled_task_create'),
    
    # Contact messages
    path('contact-messages/', views.ContactMessageListView.as_view(), name='contact_messages'),
    path('contact-messages/<int:pk>/', views.ContactMessageDetailView.as_view(), name='contact_message_detail'),
    path('contact-messages/<int:pk>/respond/', views.ContactMessageResponseView.as_view(), name='contact_message_respond'),
    
    # Reports
    path('reports/appointments/', views.AppointmentReportView.as_view(), name='appointment_report'),
    path('reports/doctors/', views.DoctorReportView.as_view(), name='doctor_report'),
    path('reports/patients/', views.PatientReportView.as_view(), name='patient_report'),
    path('reports/prescriptions/', views.PrescriptionReportView.as_view(), name='prescription_report'),
    path('reports/generate/', views.GenerateReportView.as_view(), name='generate_report'),
    
    # Utilities
    path('health-check/', views.HealthCheckView.as_view(), name='health_check'),
] 