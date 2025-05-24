from django.db import models
from medicalpro.accounts.models import User
from django.core.validators import MinValueValidator


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'specialties'
        verbose_name_plural = 'Specialties'
        ordering = ['name']


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name='doctors')
    license_number = models.CharField(max_length=50, unique=True)
    biography = models.TextField(blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.specialty})"
    
    @property
    def full_name(self):
        return f"Dr. {self.user.get_full_name()}"
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def phone(self):
        return self.user.profile.phone
    
    class Meta:
        db_table = 'doctors'
        ordering = ['user__profile__first_name', 'user__profile__last_name']


class DoctorAvailability(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.doctor} - {self.day_of_week} {self.start_time} to {self.end_time}"
    
    class Meta:
        db_table = 'doctor_availability'
        verbose_name_plural = 'Doctor availabilities'
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']


class DoctorUnavailability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='unavailability')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.doctor} - Unavailable from {self.start_datetime} to {self.end_datetime}"
    
    class Meta:
        db_table = 'doctor_unavailability'
        verbose_name_plural = 'Doctor unavailabilities'
        ordering = ['start_datetime']


class Qualification(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='qualifications')
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year_of_completion = models.PositiveIntegerField()
    document = models.FileField(upload_to='doctor_qualifications/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.degree} from {self.institution} ({self.year_of_completion})"
    
    class Meta:
        db_table = 'qualifications'
        ordering = ['-year_of_completion']


class Certificate(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='certificates')
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    certificate_number = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to='doctor_certificates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} issued by {self.issuing_organization}"
    
    @property
    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.expiry_date:
            return today <= self.expiry_date
        return True
    
    class Meta:
        db_table = 'certificates'
        ordering = ['-issue_date']


class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='reviews')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, 
                                   related_name='review', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    review_text = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # Requires approval before being visible
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Review for {self.doctor} by {self.patient if not self.is_anonymous else 'Anonymous'}"
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ('doctor', 'patient', 'appointment') 