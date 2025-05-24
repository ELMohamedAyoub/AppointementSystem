import json
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from medicalpro.accounts.models import Notification, User

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


def send_notification(user_id, title, message, notification_type=None, related_entity=None, related_id=None):
    """
    Send a notification to a user via database and WebSocket.
    
    Args:
        user_id (int): The ID of the user to notify
        title (str): The notification title
        message (str): The notification message
        notification_type (str, optional): Type of notification (e.g., 'appointment', 'message')
        related_entity (str, optional): Related entity type (e.g., 'appointments', 'prescriptions')
        related_id (int, optional): ID of the related entity
    
    Returns:
        Notification: The created notification object
    """
    try:
        # Create database notification
        notification = Notification.objects.create(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            related_entity=related_entity,
            related_id=related_id
        )
        
        # Send WebSocket notification
        notification_data = {
            'type': 'notification_message',
            'message': {
                'id': notification.id,
                'title': title,
                'message': message,
                'type': notification_type,
                'related_entity': related_entity,
                'related_id': related_id,
                'created_at': notification.created_at.isoformat()
            }
        }
        
        room_group_name = f'user_{user_id}_notifications'
        
        try:
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                notification_data
            )
        except Exception as e:
            logger.error(f"WebSocket notification error: {str(e)}")
        
        return notification
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        return None


def send_email_notification(user_email, subject, template_name, context=None):
    """
    Send an email notification to a user.
    
    Args:
        user_email (str): The recipient's email address
        subject (str): The email subject
        template_name (str): The name of the template to use
        context (dict, optional): Context data for the template
    
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    if not context:
        context = {}
    
    try:
        html_message = render_to_string(f'emails/{template_name}.html', context)
        plain_message = render_to_string(f'emails/{template_name}.txt', context)
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def log_error(message, level='ERROR', user=None, module=None, function=None, line_number=None, 
             traceback=None, request=None):
    """
    Log an error to the database.
    
    Args:
        message (str): Error message
        level (str): Error level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        user (User, optional): The user who triggered the error
        module (str, optional): Module where the error occurred
        function (str, optional): Function where the error occurred
        line_number (int, optional): Line number where the error occurred
        traceback (str, optional): Error traceback
        request (HttpRequest, optional): The request that triggered the error
    """
    from medicalpro.core.models import ErrorLog
    
    try:
        error_log = ErrorLog(
            user=user,
            level=level,
            message=message,
            traceback=traceback,
            module=module,
            function=function,
            line_number=line_number
        )
        
        if request:
            error_log.ip_address = get_client_ip(request)
            error_log.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Sanitize request data to avoid sensitive information
            request_data = {
                'method': request.method,
                'path': request.path,
                'GET': dict(request.GET.items()),
            }
            
            if request.method in ('POST', 'PUT', 'PATCH'):
                try:
                    # Clone request.POST and sanitize sensitive fields
                    post_data = dict(request.POST.items())
                    for sensitive_field in ['password', 'token', 'key', 'secret', 'credit_card']:
                        for key in list(post_data.keys()):
                            if sensitive_field in key.lower():
                                post_data[key] = '********'
                    request_data['POST'] = post_data
                except Exception:
                    request_data['POST'] = 'Unable to parse POST data'
            
            error_log.request_data = request_data
        
        error_log.save()
        
        # Also log to the logging system
        getattr(logger, level.lower())(message)
        
        return error_log
    except Exception as e:
        logger.error(f"Failed to log error to database: {str(e)}")
        logger.error(message)
        return None


def get_client_ip(request):
    """Get the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_system_setting(key, default=None):
    """
    Get a system setting from the database.
    
    Args:
        key (str): Setting key
        default: Default value if setting doesn't exist
    
    Returns:
        The setting value or default
    """
    from medicalpro.core.models import SystemSetting
    
    try:
        setting = SystemSetting.objects.get(key=key)
        return setting.value
    except SystemSetting.DoesNotExist:
        return default
    except Exception as e:
        logger.error(f"Error getting system setting {key}: {str(e)}")
        return default


def set_system_setting(key, value, description=None):
    """
    Set a system setting in the database.
    
    Args:
        key (str): Setting key
        value: Setting value
        description (str, optional): Setting description
    
    Returns:
        SystemSetting: The updated or created setting
    """
    from medicalpro.core.models import SystemSetting
    
    try:
        setting, created = SystemSetting.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'description': description
            }
        )
        return setting
    except Exception as e:
        logger.error(f"Error setting system setting {key}: {str(e)}")
        return None 