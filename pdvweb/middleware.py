# middleware.py
from datetime import timedelta
from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone

class InactivityLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            if request.path != '/realizar_venda/':
                last_activity = request.session.get('last_activity')
                if last_activity:
                    last_activity = timezone.datetime.fromisoformat(last_activity)
                    idle_time = timezone.now() - last_activity
                    if idle_time > timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES):
                        logout(request)
            request.session['last_activity'] = str(timezone.now())
        return response
