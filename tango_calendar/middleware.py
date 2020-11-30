from django.utils.timezone import activate, deactivate, get_current_timezone_name


class TimezoneAwareMiddleware:
    """Activate user timezone"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz = getattr(request.user, "timezone", get_current_timezone_name())
        activate(tz)
        response = self.get_response(request)
        deactivate()
        return response