from django.db import models
from django.conf import settings
from django.utils import timezone


class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.key
    
    class Meta:
        db_table = 'system_settings'
        ordering = ['key']


class APILog(models.Model):
    REQUEST_METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                           null=True, blank=True, related_name='api_logs')
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=REQUEST_METHOD_CHOICES)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.PositiveSmallIntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    execution_time = models.FloatField(null=True, blank=True)  # in milliseconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"
    
    class Meta:
        db_table = 'api_logs'
        ordering = ['-created_at']


class ErrorLog(models.Model):
    ERROR_LEVEL_CHOICES = (
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                           null=True, blank=True, related_name='error_logs')
    level = models.CharField(max_length=10, choices=ERROR_LEVEL_CHOICES)
    message = models.TextField()
    traceback = models.TextField(blank=True, null=True)
    module = models.CharField(max_length=255, blank=True, null=True)
    function = models.CharField(max_length=255, blank=True, null=True)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    request_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.level}: {self.message[:50]}"
    
    class Meta:
        db_table = 'error_logs'
        ordering = ['-created_at']


class ScheduledTask(models.Model):
    TASK_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Running', 'Running'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    TASK_TYPE_CHOICES = (
        ('AppointmentReminder', 'AppointmentReminder'),
        ('DataBackup', 'DataBackup'),
        ('ReportGeneration', 'ReportGeneration'),
        ('SystemMaintenance', 'SystemMaintenance'),
        ('Other', 'Other'),
    )
    
    name = models.CharField(max_length=255)
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='Pending')
    parameters = models.JSONField(null=True, blank=True)
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.task_type}) - {self.status}"
    
    @property
    def is_due(self):
        return self.scheduled_at <= timezone.now()
    
    @property
    def execution_time(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    class Meta:
        db_table = 'scheduled_tasks'
        ordering = ['-scheduled_at']


class ContactMessage(models.Model):
    MESSAGE_STATUS_CHOICES = (
        ('New', 'New'),
        ('Read', 'Read'),
        ('Responded', 'Responded'),
        ('Archived', 'Archived'),
    )
    
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS_CHOICES, default='New')
    response = models.TextField(blank=True, null=True)
    responded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='contact_responses')
    responded_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} from {self.name}"
    
    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at'] 