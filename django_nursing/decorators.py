from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils.timezone import now
from django.core.cache import cache
from datetime import timedelta

def login_limit(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'POST':
            username = request.POST.get('username')
            key = f'login_attempts_{username}'
            attempts = cache.get(key, {'count': 0, 'last_attempt': now()})
            
            # Check if the number of attempts is exceeded
            if attempts['count'] > 5 and now() < attempts['last_attempt'] + timedelta(minutes=15):
                return render(request,'accounts/account-locked.html')

        return view_func(request, *args, **kwargs)
    return _wrapped_view