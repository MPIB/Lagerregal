from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from django_auth_ldap.backend import populate_user
        from .signals import populate_main_department
        populate_user.connect(populate_main_department)
