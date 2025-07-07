import logging
import traceback
from django.http import JsonResponse
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

class CustomExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            response = {'error': exception.message_dict if hasattr(exception, 'message_dict') else str(exception)}
            status_code = 400

        elif isinstance(exception, PermissionDenied):
            response = {'error': 'Permission denied.'}
            status_code = 403

        elif isinstance(exception, Http404):
            response = {'error': 'Resource not found.'}
            status_code = 404

        else:
            response = {'error': 'An unexpected error occurred.'}
            status_code = 500

            if not settings.DEBUG:
                logger.error(f"Unhandled exception: {str(exception)}")
                logger.error(traceback.format_exc())
            else:
                
                response['details'] = traceback.format_exc()

        return JsonResponse(response, status=status_code)
