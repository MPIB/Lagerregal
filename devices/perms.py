from permission.logics import PermissionLogic

__author__ = 'viirus'


class DevicePermissionLogic(PermissionLogic):
    def has_perm(self, user_obj, perm, obj=None):
        if perm == "devices.read_device" and not obj.is_private:
            return True
        if user_obj.is_active and user_obj.has_perm(perm):
            return obj.department in user_obj.departments.all()


PERMISSION_LOGICS = (
    ('devices.Device', DevicePermissionLogic()),
)
