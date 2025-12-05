from django.core.cache import cache
from django.utils.timezone import now
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class LoginAttemptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path == '/accounts/login/user':
            username = request.POST.get('username')
            if username:
                key = f'login_attempts_{username}'
                attempts = cache.get(key, {'count': 0, 'last_attempt': now()})
                logger.debug(f"Login attempts before processing: {attempts}")
                
                # Check if 15 minutes have passed since the last attempt
                if now() > attempts['last_attempt'] + timedelta(minutes=15):
                    attempts = {'count': 0, 'last_attempt': now()}  # Reset count after 15 minutes
                
                attempts['count'] += 1
                attempts['last_attempt'] = now()
                cache.set(key, attempts, timeout=900)  # Store the attempts with a 15-minute timeout
                logger.debug(f"Login attempts after processing: {attempts}")

        response = self.get_response(request)
        return response