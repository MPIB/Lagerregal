from django.conf import settings
from django.template import Library

register = Library()


@register.filter('theme_path')
def theme_path(user):
    theme = getattr(user, 'theme', None) or settings.THEMES[0]
    return 'bootswatch/%s/bootstrap.min.css' % theme
