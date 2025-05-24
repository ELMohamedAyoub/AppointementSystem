from django.db import models
from medicalpro.patients.models import Patient
from medicalpro.doctors.models import Doctor
from medicalpro.appointments.models import Appointment


class Medication(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'medications'
        ordering = ['name']


class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    prescription_date = models.DateField()
    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor} on {self.prescription_date}"
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-prescription_date']


class PrescriptionMedication(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medications')
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, related_name='prescriptions')
    dosage = models.CharField(max_length=100)  # e.g., "10mg"
    frequency = models.CharField(max_length=100)  # e.g., "Twice daily", "Every 6 hours"
    duration = models.CharField(max_length=100)  # e.g., "7 days", "2 weeks"
    instructions = models.TextField(blank=True, null=True)  # e.g., "Take with food"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.medication.name} - {self.dosage} - {self.frequency}"
    
    class Meta:
        db_table = 'prescription_medications'
        ordering = ['prescription', 'medication__name']


class PrescriptionDocument(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='prescription_documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} for {self.prescription}"
    
    class Meta:
        db_table = 'prescription_documents'
        ordering = ['-created_at']


class PrescriptionTemplate(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescription_templates')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    diagnosis_template = models.TextField(blank=True, null=True)
    notes_template = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.doctor}"
    
    class Meta:
        db_table = 'prescription_templates'
        ordering = ['doctor', 'name']


class TemplateMedication(models.Model):
    template = models.ForeignKey(PrescriptionTemplate, on_delete=models.CASCADE, related_name='medications')
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, related_name='templates')
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.medication.name} for {self.template.name}"
    
    class Meta:
        db_table = 'template_medications'
        ordering = ['template', 'medication__name']


class MedicationInteraction(models.Model):
    SEVERITY_CHOICES = (
        ('Minor', 'Minor'),
        ('Moderate', 'Moderate'),
        ('Major', 'Major'),
        ('Severe', 'Severe'),
    )
    
    medication1 = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='interactions_as_first')
    medication2 = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='interactions_as_second')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField()
    source = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Interaction: {self.medication1} and {self.medication2} - {self.severity}"
    
    class Meta:
        db_table = 'medication_interactions'
        unique_together = [['medication1', 'medication2']] 