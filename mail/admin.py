from django.contrib import admin

from . import models

admin.site.register(models.MailTemplate)
admin.site.register(models.MailTemplateRecipient)
admin.site.register(models.MailHistory)
