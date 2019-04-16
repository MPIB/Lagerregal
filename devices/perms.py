from __future__ import unicode_literals

from permission.logics import PermissionLogic

__author__ = 'viirus'


class DevicePermissionLogic(PermissionLogic):
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_active and user_obj.has_perm(perm):
            try:
                if not obj.is_private:
                    if perm == "devices.read_device":
                        return True
            except:
                pass
            return obj.department in user_obj.departments.all()


PERMISSION_LOGICS = (
    ('devices.Device', DevicePermissionLogic()),
)
