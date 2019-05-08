from django.contrib.auth import mixins as auth_mixins


class PermissionRequiredMixin(auth_mixins.PermissionRequiredMixin):
    def get_permission_object(self):
        return None

    def has_permission(self):
        perms = self.get_permission_required()
        permission_object = self.get_permission_object()
        return self.request.user.has_perms(perms, obj=permission_object)
