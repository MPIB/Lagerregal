from django.utils import timezone

class TimezoneMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.user.timezone != None:
                timezone.activate(request.user.timezone)