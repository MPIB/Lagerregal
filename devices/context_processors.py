from django.conf import settings  # import the settings file


def get_settings(request):
    return {'SITE_NAME': settings.SITE_NAME,
            'LABEL_TEMPLATES': settings.LABEL_TEMPLATES}
