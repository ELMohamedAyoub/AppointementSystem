from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from medicalpro.accounts.models import User
from medicalpro.patients.models import Patient
from medicalpro.doctors.models import Doctor


class AppointmentStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'appointment_status'
        verbose_name_plural = 'Appointment statuses'
        ordering = ['name']


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.ForeignKey(AppointmentStatus, on_delete=models.PROTECT, related_name='appointments')
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_followup = models.BooleanField(default=False)
    previous_appointment = models.ForeignKey('self', on_delete=models.SET_NULL, 
                                           related_name='followup_appointments', 
                                           null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_appointments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date} at {self.start_time}"
    
    def clean(self):
        # Ensure start_time is before end_time
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(_('Start time must be before end time.'))
        
        # Check for time slot conflicts
        conflicts = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            status__name__in=['Scheduled', 'Confirmed', 'Waiting', 'In Progress']
        ).exclude(id=self.id).filter(
            Q(start_time__lt=self.end_time, end_time__gt=self.start_time) |
            Q(start_time=self.start_time, end_time=self.end_time)
        )
        
        if conflicts.exists():
            raise ValidationError(_('This time slot conflicts with another appointment.'))
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-start_time']


class AppointmentDocument(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='appointment_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_appointment_documents')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} for {self.appointment}"
    
    class Meta:
        db_table = 'appointment_documents'
        ordering = ['-created_at']


class AppointmentReminder(models.Model):
    REMINDER_TYPE_CHOICES = (
        ('Email', 'Email'),
        ('SMS', 'SMS'),
        ('Both', 'Both'),
    )
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField()
    reminder_type = models.CharField(max_length=5, choices=REMINDER_TYPE_CHOICES, default='Email')
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder for {self.appointment} at {self.reminder_time}"
    
    class Meta:
        db_table = 'appointment_reminders'
        ordering = ['reminder_time']


class CancellationReason(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='cancellation')
    reason = models.TextField()
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cancelled_appointments')
    cancellation_fee_applied = models.BooleanField(default=False)
    cancellation_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cancellation for {self.appointment}"
    
    class Meta:
        db_table = 'cancellation_reasons'
        ordering = ['-created_at']


class WaitingList(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='waiting_entries')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='waiting_entries')
    requested_date = models.DateField(null=True, blank=True)  # Optional specific date
    date_range_start = models.DateField(null=True, blank=True)  # Start of date range preference
    date_range_end = models.DateField(null=True, blank=True)  # End of date range preference
    time_preference = models.CharField(max_length=100, blank=True, null=True)  # e.g., "Morning", "Afternoon"
    notes = models.TextField(blank=True, null=True)
    priority = models.PositiveSmallIntegerField(default=0)  # Higher number = higher priority
    is_fulfilled = models.BooleanField(default=False)
    fulfilled_by_appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, 
                                               related_name='from_waiting_list', 
                                               null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_waiting_entries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient} waiting for {self.doctor}"
    
    class Meta:
        db_table = 'waiting_list'
        ordering = ['-priority', 'created_at'] 