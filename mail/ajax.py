from __future__ import unicode_literals

import json

from django.views.generic.base import View
from django.http import HttpResponse

import six

from mail.models import USAGES
from mail.models import MailTemplate


class LoadChoices(View):
    def post(self, request, *args, **kwargs):
        used = MailTemplate.objects.values_list('usage', flat=True)
        valid = {str(x): six.text_type(y) for x, y in USAGES if not any(z in x for z in used)}
        valid.update({'': '--------'})
        return(HttpResponse(json.dumps(valid), content_type="application/json"))
