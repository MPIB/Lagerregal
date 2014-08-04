# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator
from django.conf import settings
import pytz
from django.core.urlresolvers import reverse

# Create your models here.
class Lageruser(AbstractUser):
    language = models.CharField(max_length=10, null=True, blank=True,
                                choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0])
    timezone = models.CharField(max_length=50, null=True, blank=True,
                                choices=[(tz, tz) for tz in pytz.common_timezones], default=None)
    pagelength = models.IntegerField(validators=[
        MaxValueValidator(250)
    ], default=30)
    avatar = models.ImageField(upload_to="avatars", blank=True, null=True)

    main_department = models.ForeignKey("users.Department", null=True, blank=True)
    departments = models.ManyToManyField("users.Department", null=True, blank=True, through='users.DepartmentUser',
                                         related_name="members")

    def __unicode__(self):
        if self.first_name != "" and self.last_name != "":
            return u"{0} {1}".format(self.first_name, self.last_name)
        else:
            return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = (
            ("read_user", _("Can read User")),
        )

    def get_absolute_url(self):
        return reverse('userprofile', kwargs={'pk': self.pk})



class Department(models.Model):
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        permissions = (
            ("read_department", _("Can read Departments")),
            ("add_department_user", _("Can add a User to a Department")),
            ("delete_department_user", _("Can remove a User from a Department")),
        )


class DepartmentUser(models.Model):
    user = models.ForeignKey(Lageruser)
    department = models.ForeignKey(Department)
    role = models.CharField(choices=(("a", _("Admin")), ("m", _("Member"))), default="a", max_length=1)
    member_since = models.DateTimeField(auto_now_add=True)