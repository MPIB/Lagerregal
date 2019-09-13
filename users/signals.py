import re

from django.conf import settings

from .models import Department
from .models import DepartmentUser


def get_department_name(ldap_user):
    value = ldap_user.attrs[settings.AUTH_LDAP_DEPARTMENT_FIELD]
    return re.findall(settings.AUTH_LDAP_DEPARTMENT_REGEX, value)[-1]


def populate_main_department(user, ldap_user, **kwargs):
    department_name = get_department_name(ldap_user)
    department, __ = Department.objects.get_or_create(name=department_name)

    user.main_department = department
    user.save()

    if user.main_department not in user.departments.all():
        DepartmentUser.objects.create(
            user=user, department=user.main_department, role="m"
        )
