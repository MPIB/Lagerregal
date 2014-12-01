# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator
from django.conf import settings
import pytz
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django_auth_ldap.backend import populate_user
from django.conf import settings
import re
import datetime

class Lageruser(AbstractUser):
    language = models.CharField(max_length=10, null=True, blank=True,
                                choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0])
    timezone = models.CharField(max_length=50, null=True, blank=True,
                                choices=[(tz, tz) for tz in pytz.common_timezones], default=None)
    pagelength = models.IntegerField(validators=[
        MaxValueValidator(250)
    ], default=30)
    avatar = models.ImageField(upload_to="avatars", blank=True, null=True)
    expiration_date = models.DateField(null=True, blank=True)

    main_department = models.ForeignKey("users.Department", null=True, blank=True, on_delete=models.SET_NULL)
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

    @staticmethod
    def users_from_departments(departments=[]):
        if len(departments) == 0:
            return Lageruser.objects.all()
        return Lageruser.objects.filter(departments__in=departments)


@receiver(populate_user)
def populate_ldap_user(sender, signal, user, ldap_user, **kwargs):
    AUTH_LDAP_DEPARTMENT_REGEX = getattr(settings, "AUTH_LDAP_DEPARTMENT_REGEX", None)
    if AUTH_LDAP_DEPARTMENT_REGEX != None and user.main_department == None:
        AUTH_LDAP_DEPARTMENT_FIELD = getattr(settings, "AUTH_LDAP_DEPARTMENT_REGEX", None)
        if AUTH_LDAP_DEPARTMENT_FIELD:
            fullname = ldap_user.attrs["distinguishedname"][0]
            match = re.compile(AUTH_LDAP_DEPARTMENT_REGEX).search(fullname)
            if match:
                department_name = match.group(1)
                try:
                    department = Department.objects.get(name=department_name)
                except:
                    department = Department(name=department_name)
                    department.save()
                if not department in user.departments.all():
                    du = DepartmentUser(user=user, department=department, role="m")
                    du.save()
                user.main_department = department

    if "accountExpires" in ldap_user.attrs:
        if int(ldap_user.attrs["accountExpires"][0]) > 0:
            expires_timestamp = (int(ldap_user.attrs["accountExpires"][0])/10000000)-11644473600
            try:
                expires_date = datetime.date.fromtimestamp(expires_timestamp)
            except StandardError:
                expires_date = None
            user.expiration_date = expires_date

            if user.expiration_date:
                if user.expiration_date < datetime.date.today():
                    user.is_active = False
    user.save()


class Department(models.Model):
    name = models.CharField(max_length=40, unique=True)

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
