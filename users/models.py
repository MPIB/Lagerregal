import logging
import re
from datetime import date

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import pytz
from django_auth_ldap.backend import populate_user

from Lagerregal import utils


class Lageruser(AbstractUser):
    language = models.CharField(max_length=10, null=True, blank=True,
                                choices=settings.LANGUAGES, default=settings.LANGUAGES[0][0])
    theme = models.CharField(max_length=50, blank=True,
                             choices=[(theme, theme) for theme in settings.THEMES])
    timezone = models.CharField(max_length=50, null=True, blank=True,
                                choices=[(tz, tz) for tz in pytz.common_timezones], default=None)
    pagelength = models.IntegerField(validators=[
        MaxValueValidator(250)
    ], default=30)
    avatar = models.ImageField(upload_to=utils.get_file_location, blank=True, null=True)
    expiration_date = models.DateField(null=True, blank=True)

    main_department = models.ForeignKey("users.Department", null=True, blank=True, on_delete=models.SET_NULL)
    departments = models.ManyToManyField("users.Department", blank=True, through='users.DepartmentUser',
                                         related_name="members")

    def __str__(self):
        if self.first_name != "" and self.last_name != "":
            return "{0} {1}".format(self.first_name, self.last_name)
        else:
            return self.username

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['username']

    def get_absolute_url(self):
        return reverse('userprofile', kwargs={'pk': self.pk})

    def clean(self):
        # initial ldap population returns a positive int as string
        # will be set correctly later by populate_ldap_user() / ldapimport cmd
        self.expiration_date = None

    @staticmethod
    def users_from_departments(departments=[]):
        if len(departments) == 0:
            return Lageruser.objects.all()
        return Lageruser.objects.filter(departments__in=departments)


@receiver(populate_user)
def populate_ldap_user(sender, signal, user, ldap_user, **kwargs):
    """
    this signal is sent after the user object has been created, to override/add specific fields

    see: https://pythonhosted.org/django-auth-ldap/users.html
    """
    if settings.DEBUG:
        logger = logging.getLogger('django_auth_ldap')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    if "accountExpires" in ldap_user.attrs:
        expiration_date = utils.convert_ad_accountexpires(int(ldap_user.attrs['accountExpires'][0]))
        user.expiration_date = expiration_date

        if user.expiration_date and user.expiration_date < date.today():
            user.is_active = False

    AUTH_LDAP_DEPARTMENT_REGEX = getattr(settings, "AUTH_LDAP_DEPARTMENT_REGEX", None)
    if AUTH_LDAP_DEPARTMENT_REGEX is not None and user.main_department is None:
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
                # departments.all() needs an id
                # so we save a newly created user object first
                if user._state.adding:
                    user.save()
                if department not in user.departments.all():
                    du = DepartmentUser(user=user, department=department, role="m")
                    du.save()
                user.main_department = department

    user.save()


class Department(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        permissions = (
            ("add_department_user", _("Can add a User to a Department")),
            ("delete_department_user", _("Can remove a User from a Department")),)


class DepartmentUser(models.Model):
    user = models.ForeignKey(Lageruser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.CharField(choices=(("a", _("Admin")), ("m", _("Member"))), default="a", max_length=1)
    member_since = models.DateTimeField(auto_now_add=True)
