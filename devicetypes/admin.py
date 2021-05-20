from django.contrib import admin

from . import models

admin.site.register(models.Type)
admin.site.register(models.TypeAttribute)
admin.site.register(models.TypeAttributeValue)
