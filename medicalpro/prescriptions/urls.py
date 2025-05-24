from django.urls import path

from medicalpro.prescriptions import views

urlpatterns = [
    # Prescriptions
    path('', views.PrescriptionListView.as_view(), name='prescription_list'),
    path('<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('create/', views.PrescriptionCreateView.as_view(), name='prescription_create'),
    path('<int:pk>/update/', views.PrescriptionUpdateView.as_view(), name='prescription_update'),
    
    # Prescription medications
    path('<int:prescription_id>/medications/', views.PrescriptionMedicationListView.as_view(), name='prescription_medication_list'),
    path('<int:prescription_id>/medications/<int:pk>/', views.PrescriptionMedicationDetailView.as_view(), name='prescription_medication_detail'),
    path('<int:prescription_id>/medications/add/', views.PrescriptionMedicationCreateView.as_view(), name='prescription_medication_create'),
    path('<int:prescription_id>/medications/<int:pk>/update/', views.PrescriptionMedicationUpdateView.as_view(), name='prescription_medication_update'),
    
    # Prescription documents
    path('<int:prescription_id>/documents/', views.PrescriptionDocumentListView.as_view(), name='prescription_document_list'),
    path('<int:prescription_id>/documents/<int:pk>/', views.PrescriptionDocumentDetailView.as_view(), name='prescription_document_detail'),
    path('<int:prescription_id>/documents/create/', views.PrescriptionDocumentCreateView.as_view(), name='prescription_document_create'),
    
    # Medications
    path('medications/', views.MedicationListView.as_view(), name='medication_list'),
    path('medications/<int:pk>/', views.MedicationDetailView.as_view(), name='medication_detail'),
    path('medications/create/', views.MedicationCreateView.as_view(), name='medication_create'),
    path('medications/<int:pk>/update/', views.MedicationUpdateView.as_view(), name='medication_update'),
    
    # Medication interactions
    path('interactions/', views.MedicationInteractionListView.as_view(), name='medication_interaction_list'),
    path('interactions/<int:pk>/', views.MedicationInteractionDetailView.as_view(), name='medication_interaction_detail'),
    path('interactions/check/', views.CheckMedicationInteractionsView.as_view(), name='check_medication_interactions'),
    
    # Prescription templates
    path('templates/', views.PrescriptionTemplateListView.as_view(), name='prescription_template_list'),
    path('templates/<int:pk>/', views.PrescriptionTemplateDetailView.as_view(), name='prescription_template_detail'),
    path('templates/create/', views.PrescriptionTemplateCreateView.as_view(), name='prescription_template_create'),
    path('templates/<int:pk>/update/', views.PrescriptionTemplateUpdateView.as_view(), name='prescription_template_update'),
    
    # Template medications
    path('templates/<int:template_id>/medications/', views.TemplateMedicationListView.as_view(), name='template_medication_list'),
    path('templates/<int:template_id>/medications/<int:pk>/', views.TemplateMedicationDetailView.as_view(), name='template_medication_detail'),
    path('templates/<int:template_id>/medications/add/', views.TemplateMedicationCreateView.as_view(), name='template_medication_create'),
    
    # Patient prescription history
    path('patient/<int:patient_id>/', views.PatientPrescriptionHistoryView.as_view(), name='patient_prescription_history'),
    
    # Print and PDF generation
    path('<int:pk>/print/', views.PrescriptionPrintView.as_view(), name='prescription_print'),
    path('<int:pk>/pdf/', views.PrescriptionPDFView.as_view(), name='prescription_pdf'),
] 