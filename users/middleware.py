from __future__ import unicode_literals

from django.utils import timezone


class TimezoneMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if user.timezone is not None:
                timezone.activate(user.timezone)
        return self.get_response(request)
