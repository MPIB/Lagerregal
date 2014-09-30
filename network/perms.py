__author__ = 'viirus'
from permission.logics import PermissionLogic
from permission.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied

class IPAddressPermissionLogic(PermissionLogic):
    def __init__(self,
                 field_name=None,
                 any_permission=None,
                 change_permission=None,
                 delete_permission=None):

        self.field_name = field_name
        self.any_permission = any_permission
        self.change_permission = change_permission
        self.delete_permission = delete_permission

        if self.field_name is None:
            self.field_name = \
                settings.PERMISSION_DEFAULT_CPL_FIELD_NAME
        if self.any_permission is None:
            self.any_permission = True
        if self.change_permission is None:
            self.change_permission = True
        if self.delete_permission is None:
            self.delete_permission = True

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
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

