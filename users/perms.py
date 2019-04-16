from __future__ import unicode_literals

from permission.logics import PermissionLogic

__author__ = 'viirus'


class DepartmentPermissionLogic(PermissionLogic):
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_active:
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


PERMISSION_LOGICS = (
    ('users.Department', DepartmentPermissionLogic()),
)
