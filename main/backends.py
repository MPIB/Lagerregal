from django.conf import settings

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
        if obj is None:
            return False

        if perm == 'devices.view_device' and isinstance(obj, Device):
            public_devices = Device.objects.filter(**settings.PUBLIC_DEVICES_FILTER)
            if public_devices.filter(pk=obj.pk).exists():
                return True

        if user_obj.is_active and user_obj.has_perm(perm):
            if isinstance(obj, Department):
                if obj in user_obj.departments.all():
                    departmentuser = user_obj.departmentuser_set.get(department=obj)
                    if departmentuser.role == 'a':
                        return True

            elif isinstance(obj, IpAddress):
                if perm == 'network.view_ipaddress':
                    return True
                else:
                    return obj.department in user_obj.departments.all()

            elif isinstance(obj, Device):
                return (
                    obj.department in user_obj.departments.all()
                    or (perm == 'devices.view_device' and not obj.is_private)
                )
