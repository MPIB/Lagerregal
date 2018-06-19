from __future__ import unicode_literals

__author__ = 'viirus'
from permission.logics import PermissionLogic
from permission.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied


class DepartmentPermissionLogic(PermissionLogic):
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
            self.change_permission = \
                settings.PERMISSION_DEFAULT_CPL_CHANGE_PERMISSION
        if self.delete_permission is None:
            self.delete_permission = \
                settings.PERMISSION_DEFAULT_CPL_DELETE_PERMISSION

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            return False

        if obj is None:
            return False
        elif user_obj.is_active:
            if obj in user_obj.departments.all():
                    department_membership = user_obj.departmentuser_set.get(department=obj)
                    if department_membership.role == "a":
                        return True
            try:
                if obj.department in user_obj.departments.all():
                    department_membership = user_obj.departmentuser_set.get(department=obj.department)
                    if department_membership.role == "a":
                        return True
            except TypeError:
                return False

        return False


PERMISSION_LOGICS = (
    ('users.Department', DepartmentPermissionLogic()),
)
