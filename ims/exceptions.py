from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled

def custom_exception_handler(exc, context):
    """
    Custom exception handler providing better, more user-friendly
    error messages for throttling cases.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if isinstance(exc, Throttled):
        # Add user-friendly details to throttled responses
        throttle_instance = getattr(context['view'], 'throttle_classes', [])
        throttle_class_name = throttle_instance[0].__name__ if throttle_instance else None
        
        custom_error_messages = {
            'FeedbackRateThrottle': 'You have reached the daily limit for submitting feedback. Please try again tomorrow.',
            'JobApplicationRateThrottle': 'You have reached the daily limit for job applications. Please try again tomorrow.',
            'UserRateThrottle': f'Too many requests. Please try again in {exc.wait} seconds.',
            'AnonRateThrottle': 'Too many anonymous requests. Please try again later or log in.',
        }
        
        wait_time = exc.wait
        error_message = custom_error_messages.get(
            throttle_class_name, 
            f'Request was throttled. Expected available in {wait_time} seconds.'
        )
        
        response.data = {
            'detail': error_message,
            'wait': wait_time
        }
    
    return response 