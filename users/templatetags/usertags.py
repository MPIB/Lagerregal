from django.conf import settings
from django.contrib.messages import constants as message_constants
from django.template import Library

register = Library()

MESSAGE_LEVEL_CLASSES = {
    message_constants.DEBUG: 'alert-warning',
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger',
}


@register.filter('theme_path')
def theme_path(user):
    theme = getattr(user, 'theme', None) or settings.THEMES[0]
    return 'bootswatch/dist/%s/bootstrap.min.css' % theme


@register.simple_tag
def has_perm(perm, user, obj=None):
    return user.has_perm(perm, obj=obj)


@register.filter
def bootstrap_message_classes(message):
    classes = ['alert', 'alert-dismissible', 'fade', 'show']
    classes.append(MESSAGE_LEVEL_CLASSES[message.level])
    classes.append(message.extra_tags or '')
    return ' '.join(classes)
