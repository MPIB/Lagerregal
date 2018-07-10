from __future__ import unicode_literals

from django.utils import timezone


class TimezoneMiddleware(object):
    @staticmethod
    def process_request(request):
        user = request.user
        if user.is_authenticated:
            if user.timezone is not None:
                timezone.activate(user.timezone)
