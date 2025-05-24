from django.urls import path

from medicalpro.appointments import views

urlpatterns = [
    # Appointments CRUD
    path('', views.AppointmentListView.as_view(), name='appointment_list'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('create/', views.AppointmentCreateView.as_view(), name='appointment_create'),
    path('<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment_update'),
    path('<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    
    # Appointment status
    path('statuses/', views.AppointmentStatusListView.as_view(), name='appointment_status_list'),
    
    # Appointment documents
    path('documents/', views.AppointmentDocumentListView.as_view(), name='appointment_document_list'),
    path('documents/<int:pk>/', views.AppointmentDocumentDetailView.as_view(), name='appointment_document_detail'),
    path('documents/create/', views.AppointmentDocumentCreateView.as_view(), name='appointment_document_create'),
    
    # Appointment reminders
    path('reminders/', views.AppointmentReminderListView.as_view(), name='appointment_reminder_list'),
    path('reminders/<int:pk>/', views.AppointmentReminderDetailView.as_view(), name='appointment_reminder_detail'),
    path('reminders/create/', views.AppointmentReminderCreateView.as_view(), name='appointment_reminder_create'),
    
    # Cancellation reasons
    path('cancellations/', views.CancellationReasonListView.as_view(), name='cancellation_reason_list'),
    path('cancellations/<int:pk>/', views.CancellationReasonDetailView.as_view(), name='cancellation_reason_detail'),
    
    # Waiting list
    path('waiting-list/', views.WaitingListView.as_view(), name='waiting_list'),
    path('waiting-list/<int:pk>/', views.WaitingListItemDetailView.as_view(), name='waiting_list_item_detail'),
    path('waiting-list/create/', views.WaitingListCreateView.as_view(), name='waiting_list_create'),
    
    # Search and filter appointments
    path('search/', views.AppointmentSearchView.as_view(), name='appointment_search'),
    path('calendar/', views.AppointmentCalendarView.as_view(), name='appointment_calendar'),
    
    # Appointment fulfillment (completing an appointment)
    path('<int:pk>/complete/', views.AppointmentCompleteView.as_view(), name='appointment_complete'),
    
    # Analytics
    path('analytics/doctor/', views.DoctorAppointmentAnalyticsView.as_view(), name='doctor_appointment_analytics'),
    path('analytics/patient/', views.PatientAppointmentAnalyticsView.as_view(), name='patient_appointment_analytics'),
] 