from django.urls import path

from medicalpro.doctors import views

urlpatterns = [
    # Doctor profiles
    path('', views.DoctorListView.as_view(), name='doctor_list'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('profile/', views.DoctorProfileView.as_view(), name='doctor_profile'),
    path('profile/update/', views.DoctorProfileUpdateView.as_view(), name='doctor_profile_update'),
    
    # Doctor availability
    path('availability/', views.DoctorAvailabilityListView.as_view(), name='doctor_availability_list'),
    path('availability/<int:pk>/', views.DoctorAvailabilityDetailView.as_view(), name='doctor_availability_detail'),
    path('availability/create/', views.DoctorAvailabilityCreateView.as_view(), name='doctor_availability_create'),
    
    # Doctor unavailability (time off, vacations, etc.)
    path('unavailability/', views.DoctorUnavailabilityListView.as_view(), name='doctor_unavailability_list'),
    path('unavailability/<int:pk>/', views.DoctorUnavailabilityDetailView.as_view(), name='doctor_unavailability_detail'),
    path('unavailability/create/', views.DoctorUnavailabilityCreateView.as_view(), name='doctor_unavailability_create'),
    
    # Specialties
    path('specialties/', views.SpecialtyListView.as_view(), name='specialty_list'),
    path('specialties/<int:pk>/', views.SpecialtyDetailView.as_view(), name='specialty_detail'),
    
    # Doctor qualifications and certifications
    path('qualifications/', views.QualificationListView.as_view(), name='qualification_list'),
    path('qualifications/<int:pk>/', views.QualificationDetailView.as_view(), name='qualification_detail'),
    path('certificates/', views.CertificateListView.as_view(), name='certificate_list'),
    path('certificates/<int:pk>/', views.CertificateDetailView.as_view(), name='certificate_detail'),
    
    # Doctor reviews
    path('reviews/', views.DoctorReviewListView.as_view(), name='doctor_review_list'),
    path('reviews/<int:pk>/', views.DoctorReviewDetailView.as_view(), name='doctor_review_detail'),
    
    # Available time slots
    path('available-slots/', views.AvailableSlotsView.as_view(), name='available_slots'),
] 