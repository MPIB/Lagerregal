# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import pystache

from users.models import Lageruser, Department


usages = {
    "new": _("New Device is created"),
    "room": _("Room is changed"),
    "owner": _("person currently lending is changed"),
    "reminder": _("Reminder that device is still owned"),
    "overdue": _("Reminder that device is overdue"),
    "trashed": _("Device is trashed")
}


class MailTemplate(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    subject = models.CharField(_('Subject'), max_length=500)
    body = models.CharField(_('Body'), max_length=10000)
    department = models.ForeignKey(Department, null=True)

    usage = models.CharField(_('Usage'), choices=usages.items(), null=True, blank=True, max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('Mailtemplate')
        verbose_name_plural = _('Mailtemplates')
        permissions = (
            ("read_mailtemplate", _("Can read Mailtemplate")),
        )

    def get_absolute_url(self):
        return reverse('mail-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('mail-edit', kwargs={'pk': self.pk})

    def send(self, request, recipients=None, data=None):
        datadict = {}
        datadict["device"] = {
            "description": data["device"].description,
            "devicetype": (data["device"].devicetype.name if data["device"].devicetype != None else ""),
            "group": data["device"].group,
            "hostname": data["device"].hostname,
            "inventoried": data["device"].inventoried,
            "inventorynumber": data["device"].inventorynumber,
            "manufacturer": data["device"].manufacturer,
            "name": data["device"].__unicode__(),
            "room": (data["device"].room.name + " (" + data["device"].room.building.name + ")" if data[
                                                                                                      "device"].room != None else ""),
            "serialnumber": data["device"].serialnumber,
            "templending": data["device"].templending,
            "trashed": data["device"].trashed,
            "webinterface": data["device"].webinterface,
            "department": data["device"].department
        }
        if data["device"].currentlending != None:
            datadict["device"]["currentlending"] = {
                "owner":data["device"].currentlending.owner.__unicode__(),
                "duedate":data["device"].currentlending.duedate,
                "lenddate":data["device"].currentlending.lenddate
            },
        else:
            datadict["device"]["currentlending"] = ""

        datadict["user"] = {
            "username": data["user"].username,
            "first_name": data["user"].first_name,
            "last_name": data["user"].last_name
        }
        if "owner" in data:
            datadict["owner"] = {
                "username": data["owner"].username,
                "first_name": data["owner"].first_name,
                "last_name": data["owner"].last_name
            }
        body = pystache.render(self.body, datadict)
        subject = pystache.render(self.subject, datadict)

        email = EmailMessage(subject=subject, body=body, to=recipients)
        email.send()
        mailhistory = MailHistory()
        mailhistory.mailtemplate = self
        mailhistory.subject = self.subject
        mailhistory.body = body
        mailhistory.sent_by = request.user
        if "device" in data:
            mailhistory.device = data["device"]
        mailhistory.save()


class MailTemplateRecipient(models.Model):
    mailtemplate = models.ForeignKey(MailTemplate, related_name='default_recipients')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return unicode(self.content_type.name + ": " + self.content_object.__unicode__())


class MailHistory(models.Model):
    mailtemplate = models.ForeignKey(MailTemplate)
    subject = models.CharField(_('Subject'), max_length=500)
    body = models.CharField(_('Body'), max_length=10000)
    sent_by = models.ForeignKey(Lageruser, null=True, on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey("devices.Device", null=True)


    def get_absolute_url(self):
        return reverse('mailhistory-detail', kwargs={'pk': self.pk})
