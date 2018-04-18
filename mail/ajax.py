from __future__ import unicode_literals
from django.views.generic.base import View
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
import json

from mail.models import MailTemplate

class LoadChoices(View):
    def post(self, request, *args, **kwargs):
        print("FUNCTION!!")
        usages = {
            "new": _("New Device is created"),
            "room": ("Room is changed"),
            "owner": _("person currently lending is changed"),
            "reminder": _("Reminder that device is still owned"),
            "overdue": _("Reminder that device is overdue"),
            "trashed": _("Device is trashed")
        }
        department = request.POST["department"]
        print "DEPARTMENT!!!!!!!"
        print department
        used = MailTemplate.objects.values_list('usage', flat=True).filter(department = department)
        print "USED!!!!!"
        print used
        valid = [x for x in usages if not any(y in x for y in used)]
        print "VALID!!!!!!!!!!"
        print valid
        # json_valid = [unicode(usages[x]) for x in valid]
        json_valid = {}
        for choice in valid:
            json_valid[choice] = unicode(usages[choice])
            print choice
            print usages[choice]
        print type(json_valid)
        print json_valid
        return(HttpResponse(json.dumps(json_valid), content_type="application/json"))
