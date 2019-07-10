"""
Since Django 1.3, media files are no longer deleted with the
corresponding model.

https://docs.djangoproject.com/en/stable/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files
"""


import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import FileField


def iter_models():
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            yield model


def iter_file_fields(model):
    for field in model._meta.get_fields():
        if isinstance(field, FileField):
            yield field


def iter_media_files():
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            yield os.path.join(root, filename)


def get_used_files():
    files = []
    for model in iter_models():
        for field in iter_file_fields(model):
            files += model.objects.values_list(field.name, flat=True)
    return [os.path.join(settings.MEDIA_ROOT, f) for f in files if f]


class Command(BaseCommand):
    help = 'Remove unused uploaded files.'

    def handle(self, *args, **options):
        used_files = get_used_files()
        for path in iter_media_files():
            if path not in used_files:
                print('Deleting', path)
                os.unlink(path)
