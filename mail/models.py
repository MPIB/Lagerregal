from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pystache

from users.models import Lageruser

USAGES = [
    ("lent", _("Device has been lent")),
    ("new", _("New Device is created")),
    ("reminder", _("Reminder that device is still owned")),
    ("returned", _("Device has been returned by user")),
    ("room", _("Room has been changed")),
    ("overdue", _("Reminder that device is overdue")),
    ("owner", _("Lending owner has been changed")),
    ("trashed", _("Device has been trashed")),
]


class MailTemplate(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    subject = models.CharField(_('Subject'), max_length=500)
    body = models.CharField(_('Body'), max_length=10000)
    usage = models.CharField(_('Usage'), choices=USAGES, null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('Mailtemplate')
        verbose_name_plural = _('Mailtemplates')

    def get_absolute_url(self):
        return reverse('mail-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('mail-edit', kwargs={'pk': self.pk})

    def send(self, request, recipients=None, data=None):
        datadict = {}
        datadict["device"] = {
            "archived": data["device"].archived,
            "created_at": data["device"].created_at,
            "creator": data["device"].creator,
            "currentlending": data["device"].currentlending,
            "department": data["device"].department,
            "description": data["device"].description,
            "devicetype": (data["device"].devicetype.name if data["device"].devicetype is not None else ""),
            "group": data["device"].group,
            "hostname": data["device"].hostname,
            "id": data["device"].id,
            "inventoried": data["device"].inventoried,
            "inventorynumber": data["device"].inventorynumber,
            "manufacturer": data["device"].manufacturer,
            "name": str(data["device"]),
            "room": '' if data["device"].room is None else '{} ({})'.format(
                data["device"].room.name,
                data["device"].room.building.name,
            ),
            "serialnumber": data["device"].serialnumber,
            "templending": data["device"].templending,
            "trashed": data["device"].trashed,
            "webinterface": data["device"].webinterface,
        }
        if data["device"].currentlending is not None:
            datadict["device"]["currentlending"] = {
                "owner": str(data["device"].currentlending.owner),
                "duedate": data["device"].currentlending.duedate,
                "lenddate": data["device"].currentlending.lenddate
            },
        else:
            datadict["device"]["currentlending"] = ""

        datadict["user"] = {
            "username": data["user"].username,
            "first_name": data["user"].first_name,
            "last_name": data["user"].last_name,
            "main_department": data["user"].main_department
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
    mailtemplate = models.ForeignKey(MailTemplate, related_name='default_recipients', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.content_type.name) + ": " + str(self.content_object)


class MailHistory(models.Model):
    mailtemplate = models.ForeignKey(MailTemplate, on_delete=models.CASCADE)
    subject = models.CharField(_('Subject'), max_length=500)
    body = models.CharField(_('Body'), max_length=10000)
    sent_by = models.ForeignKey(Lageruser, null=True, on_delete=models.SET_NULL)
    sent_at = models.DateTimeField(auto_now_add=True)
    device = models.ForeignKey("devices.Device", null=True, on_delete=models.CASCADE)
