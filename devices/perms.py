__author__ = 'viirus'
from permission.logics import PermissionLogic
from permission.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied

class DevicePermissionLogic(PermissionLogic):
    def __init__(self,
                 field_name=None,
                 any_permission=None,
                 change_permission=None,
                 delete_permission=None):
        """
        Constructor

        Parameters
        ----------
        field_name : string
            A field name of object which store the collaborators as django
            relational fields for django user model
            Default value will be taken from
            ``PERMISSION_DEFAULT_COLLABORATORS_PERMISSION_LOGIC_FIELD_NAME`` in
            settings.
        any_permission : boolean
            True for give any permission of the specified object to the
            collaborators.
            Default value will be taken from
            ``PERMISSION_DEFAULT_COLLABORATORS_PERMISSION_LOGIC_ANY_PERMISSION``
            in settings.
        change_permission : boolean
            True for give change permission of the specified object to the
            collaborators.
            It will be ignored if :attr:`any_permission` is True.
            Default value will be taken from
            ``PERMISSION_DEFAULT_COLLABORATORS_PERMISSION_LOGIC_CHANGE_PERMISSION``
            in settings.
        delete_permission : boolean
            True for give delete permission of the specified object to the
            collaborators.
            It will be ignored if :attr:`any_permission` is True.
            Default value will be taken from
            ``PERMISSION_DEFAULT_COLLABORATORS_PERMISSION_LOGIC_DELETE_PERMISSION``
            in settings.
        """
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

        change_permission = self.get_full_permission_string('change')
        delete_permission = self.get_full_permission_string('delete')

        if obj is None:
            backend = auth.get_backends()[0]
            try:
                if backend.has_perm(user_obj, perm, obj):
                    return True
            except PermissionDenied:
                return False
            return False
        elif user_obj.is_active and user_obj.has_perm(perm):
            if obj.is_private:
                if  obj.department in user_obj.departments.all():
                    return True
            else:
                if perm == "devices.read_device":
                    return True
                else:
                    return obj.department in user_obj.departments.all()
        return False




PERMISSION_LOGICS = (
    ('devices.Device', DevicePermissionLogic()),
)

