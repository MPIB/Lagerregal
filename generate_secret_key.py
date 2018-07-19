from __future__ import unicode_literals

from django.utils.crypto import get_random_string

chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
print(get_random_string(50, chars))
