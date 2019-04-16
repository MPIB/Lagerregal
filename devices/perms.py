from __future__ import unicode_literals

from django.contrib import auth
from django.core.exceptions import PermissionDenied

from permission.logics import PermissionLogic

__author__ = 'viirus'


class DevicePermissionLogic(PermissionLogic):
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated:
            return False

        if obj is None:
            backend = auth.get_backends()[0]
            try:
                if backend.has_perm(user_obj, perm, obj):
                    return True
            except PermissionDenied:
                return False
            return False
        elif user_obj.is_active and user_obj.has_perm(perm):
            try:
                if not obj.is_private:
                    if perm == "devices.read_device":
                        return True
            except:
                pass
            return obj.department in user_obj.departments.all()
        return False


PERMISSION_LOGICS = (
    ('devices.Device', DevicePermissionLogic()),
)
