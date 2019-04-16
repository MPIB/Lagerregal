from __future__ import unicode_literals

from permission.logics import PermissionLogic

__author__ = 'viirus'


class IPAddressPermissionLogic(PermissionLogic):
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated:
            return False

        if obj is None:
            return False
        elif user_obj.is_active and user_obj.has_perm(perm):
            if perm == "network.read_ipaddress":
                return True
            else:
                return obj.department in user_obj.departments.all()
        return False


PERMISSION_LOGICS = (
    ('network.IpAddress', IPAddressPermissionLogic()),
)
