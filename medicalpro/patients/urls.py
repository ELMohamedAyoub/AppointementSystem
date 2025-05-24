from django.urls import path

from medicalpro.patients import views

urlpatterns = [
    # Patient profiles
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('profile/', views.PatientProfileView.as_view(), name='patient_profile'),
    path('profile/update/', views.PatientProfileUpdateView.as_view(), name='patient_profile_update'),
    
    # Medical records
    path('medical-records/', views.MedicalRecordListView.as_view(), name='medical_record_list'),
    path('medical-records/<int:pk>/', views.MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('medical-records/create/', views.MedicalRecordCreateView.as_view(), name='medical_record_create'),
    
    # Patient notes
    path('notes/', views.PatientNoteListView.as_view(), name='patient_note_list'),
    path('notes/<int:pk>/', views.PatientNoteDetailView.as_view(), name='patient_note_detail'),
    path('notes/create/', views.PatientNoteCreateView.as_view(), name='patient_note_create'),
    
    # Insurance information
    path('insurance/', views.InsuranceInfoView.as_view(), name='insurance_info'),
    path('insurance/update/', views.InsuranceInfoUpdateView.as_view(), name='insurance_info_update'),
    
    # Family members
    path('family-members/', views.FamilyMemberListView.as_view(), name='family_member_list'),
    path('family-members/<int:pk>/', views.FamilyMemberDetailView.as_view(), name='family_member_detail'),
    path('family-members/create/', views.FamilyMemberCreateView.as_view(), name='family_member_create'),
] 