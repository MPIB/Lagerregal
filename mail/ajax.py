from __future__ import unicode_literals
from django.views.generic.base import View
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
import json
from mail.forms import MailTemplateForm

from mail.models import MailTemplate

class LoadChoices(View):
    def post(self, request, *args, **kwargs):
        usages = {
            "new": _("New Device is created"),
            "room": _("Room is changed"),
            "owner": _("person currently lending is changed"),
            "reminder": _("Reminder that device is still owned"),
            "overdue": _("Reminder that device is overdue"),
            "trashed": _("Device is trashed")
        }
        # form = MailTemplateForm(request.POST)
        form = MailTemplateForm(request.POST, initial={'department': request.POST["department"] })
        print "I AM HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        department = request.POST["department"]
        # usage = request.POST.get('')
        used = MailTemplate.objects.values_list('usage', flat=True).filter(department = department)
        valid = {str(x):y for (x,y) in usages.items() if not any(z in x for z in used)}
        # valid.update({'':  '----'})
        # valid = [x for x in usages if not any(y in x for y in used)]
        # print "VALID!!!!!!!!!!"
        # print valid
        json_valid = valid
        # json_valid = [unicode(usages[x]) for x in valid]
        json_valid = {}
        for choice in valid:
            print choice
            json_valid[choice] = unicode(usages[choice])
            # print choice
            # print usages[choice]
        # print type(json_valid)
        # print json_valid
        json_valid.update({'':  '--------'})
        # print "VALID"
        # print valid
        # print "VIEW CHOICES BEFORE"
        # a = form.fields['usage'].choices
        # print form.fields['usage'].choices
        # print type(form.fields['usage'].choices)
        # form.fields['usage'].choices = json_valid.items()
        # b = form.fields['usage'].choices
        # print "VIEW CHOICES AFTER"
        # print form.fields['usage'].choices
        # print type(form.fields['usage'].choices)
        # print "SAME??"
        # print a == b
        # print "DIFFERENCE?"
        # print list(set(a) - set(b))
        return(HttpResponse(json.dumps(json_valid), content_type="application/json"))
