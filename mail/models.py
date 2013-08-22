from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.mail import EmailMessage
from django.template import Context, Template
usages = {
    "new":_("New Device is created"),
    "room":_("Room the device is in is changed"),
    "owner":_("person currently lending is changed")
}

class MailTemplate(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    subject = models.CharField(_('Subject'), max_length=500)
    body = models.CharField(_('Body'), max_length=10000)

    usage = models.CharField(_('Usage'), choices=usages.items(), null=True, blank=True, unique=True, max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Mailtemplate')
        verbose_name_plural = _('Mailtemplates')

    def get_absolute_url(self):
        return reverse('mail-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('mail-edit', kwargs={'pk': self.pk})

    def send(self, recipients=None, data=None):
        t = Template(self.body)
        body = t.render(Context(data))
        print body, recipients
        email = EmailMessage(subject=self.subject, body=body, to=recipients)
        email.send()