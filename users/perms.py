from permission.logics import PermissionLogic

__author__ = 'viirus'


class DepartmentPermissionLogic(PermissionLogic):
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_active and user_obj.has_perm(perm):
            if obj in user_obj.departments.all():
                department_membership = user_obj.departmentuser_set.get(department=obj)
                if department_membership.role == "a":
                    return True


PERMISSION_LOGICS = (
    ('users.Department', DepartmentPermissionLogic()),
)
