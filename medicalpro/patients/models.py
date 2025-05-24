from django.db import models
from medicalpro.accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Patient(models.Model):
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, 
                                validators=[MinValueValidator(0), MaxValueValidator(300)])  # in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                validators=[MinValueValidator(0), MaxValueValidator(500)])  # in kg
    allergies = models.TextField(blank=True, null=True)
    chronic_diseases = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def phone(self):
        return self.user.profile.phone
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    record_date = models.DateField()
    record_type = models.CharField(max_length=100)
    description = models.TextField()
    file_path = models.FileField(upload_to='medical_records/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.record_type} for {self.patient} on {self.record_date}"
    
    class Meta:
        db_table = 'medical_records'
        ordering = ['-record_date']


class PatientNote(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='notes')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_notes')
    note_text = models.TextField()
    is_private = models.BooleanField(default=False)  # If True, only visible to medical staff
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Note for {self.patient} by {self.created_by}"
    
    class Meta:
        db_table = 'patient_notes'
        ordering = ['-created_at']


class InsuranceInfo(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='insurance')
    provider_name = models.CharField(max_length=255)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True, null=True)
    coverage_start_date = models.DateField()
    coverage_end_date = models.DateField(blank=True, null=True)
    primary_holder_name = models.CharField(max_length=255, blank=True, null=True)
    relation_to_primary = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Insurance for {self.patient}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.coverage_end_date:
            return self.coverage_start_date <= today <= self.coverage_end_date
        return self.coverage_start_date <= today
    
    class Meta:
        db_table = 'insurance_info'


class FamilyMember(models.Model):
    RELATION_CHOICES = (
        ('Spouse', 'Spouse'),
        ('Child', 'Child'),
        ('Parent', 'Parent'),
        ('Sibling', 'Sibling'),
        ('Other', 'Other'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=255)
    relation = models.CharField(max_length=50, choices=RELATION_CHOICES)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    is_emergency_contact = models.BooleanField(default=False)
    medical_history_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.relation} of {self.patient})"
    
    class Meta:
        db_table = 'family_members'
        ordering = ['patient', 'name'] 