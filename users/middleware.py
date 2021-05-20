from django.utils import timezone
from django.utils import translation


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if user.timezone is not None:
                timezone.activate(user.timezone)
        return self.get_response(request)


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if user.language is not None:
                translation.activate(user.language)
        return self.get_response(request)
