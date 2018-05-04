from __future__ import unicode_literals
from django.views.generic.base import View
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
import json
from mail.models import usages

from mail.models import MailTemplate

class LoadChoices(View):
    def post(self, request, *args, **kwargs):
        department = request.POST["department"]
        used = MailTemplate.objects.values_list('usage', flat=True).filter(department = department)
        valid = {str(x):y for (x,y) in usages.items() if not any(z in x for z in used)}
        json_valid = valid
        json_valid = {}
        #without using unicode(), there is an error
        for choice in valid:
            json_valid[choice] = unicode(usages[choice])
        json_valid.update({'':  '--------'})
        return(HttpResponse(json.dumps(json_valid), content_type="application/json"))
