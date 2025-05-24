import json
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.conf import settings

from medicalpro.core.utils import get_client_ip

logger = logging.getLogger(__name__)


class APILoggingMiddleware(MiddlewareMixin):
    """Middleware to log API requests and responses."""
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        self.API_URLS = ['/api/']
        self.enable_logging = getattr(settings, 'API_LOGGING_ENABLED', True)
    
    def process_request(self, request):
        if not self.enable_logging:
            return None
        
        # Only log API requests
        if not any(request.path.startswith(url) for url in self.API_URLS):
            return None
        
        # Save request start time
        request.api_request_start_time = time.time()
        
        # Try to set a request ID
        request.request_id = getattr(request, 'request_id', None) or str(int(time.time() * 1000))
        
        return None
    
    def process_response(self, request, response):
        if not self.enable_logging:
            return response
        
        # Only log API requests
        if not any(request.path.startswith(url) for url in self.API_URLS):
            return response
        
        # Skip DRF's browsable API and admin URLs
        if request.path.endswith('/') and 'text/html' in response.get('Content-Type', ''):
            return response
        
        try:
            # Calculate request execution time
            if hasattr(request, 'api_request_start_time'):
                execution_time = time.time() - request.api_request_start_time
                execution_time_ms = round(execution_time * 1000, 2)  # Convert to milliseconds
            else:
                execution_time_ms = None
            
            # Get current user
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            
            # Get request body (if it's JSON)
            request_data = None
            if request.body and request.content_type == 'application/json':
                try:
                    request_data = json.loads(request.body)
                    # Sanitize sensitive data
                    sanitized_data = {}
                    for key, value in request_data.items():
                        if key.lower() in ['password', 'token', 'key', 'secret', 'credit_card']:
                            sanitized_data[key] = '********'
                        else:
                            sanitized_data[key] = value
                    request_data = sanitized_data
                except Exception:
                    request_data = {'raw': request.body[:1000].decode('utf-8', errors='replace')}
            else:
                # For other content types, just log method and path
                request_data = {
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET.items()),
                }
            
            # Get response data (if it's JSON)
            response_data = None
            if response.get('Content-Type', '').startswith('application/json'):
                try:
                    response_body = response.content.decode('utf-8')
                    response_data = json.loads(response_body)
                    # Truncate large response data
                    if isinstance(response_data, dict) and len(response_body) > 10000:
                        response_data = {
                            'message': 'Response too large to log',
                            'size': len(response_body)
                        }
                except Exception:
                    response_data = {'error': 'Could not parse response JSON'}
            
            # Log to database
            from medicalpro.core.models import APILog
            APILog.objects.create(
                user=user,
                endpoint=request.path,
                method=request.method,
                request_data=request_data,
                response_data=response_data,
                status_code=response.status_code,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                execution_time=execution_time_ms
            )
            
            # Add execution time to response headers for debugging
            response['X-API-Execution-Time'] = f"{execution_time_ms}ms"
        
        except Exception as e:
            logger.error(f"Error in API logging middleware: {str(e)}")
        
        return response 