from devices.models import Device
from network.models import IpAddress
from users.models import Department


class LagerregalBackend:
    # NOTE: all methods except for has_perm are skipped because they are
    # not used in our application

    def authenticate(self, request, **kwargs):
        return None

    def get_user(self, user_id):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if (
            perm == 'devices.read_device'
            and isinstance(obj, Device)
            and not obj.is_private
        ):
            return True

        if user_obj.is_active and user_obj.has_perm(perm):
            if isinstance(obj, Department):
                if obj in user_obj.departments.all():
                    departmentuser = user_obj.departmentuser_set.get(department=obj)
                    if departmentuser.role == 'a':
                        return True

            elif isinstance(obj, IpAddress):
                if perm == 'network.read_ipaddress':
                    return True
                else:
                    return obj.department in user_obj.departments.all()

            elif isinstance(obj, Device):
                if user_obj.is_active and user_obj.has_perm(perm):
                    return obj.department in user_obj.departments.all()
