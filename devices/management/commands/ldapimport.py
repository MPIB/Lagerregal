# -*- coding: utf-8 -*-
import ldap
from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand

from users.models import Lageruser


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.USE_LDAP:
            l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            l.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
            users = l.search_s(*settings.LDAP_USER_SEARCH)
            created_users = 0
            for dn, user in users:
                try:
                    Lageruser.objects.get(username=user["sAMAccountName"][0])
                except Exception as e:
                    saveuser = True
                    newuser = Lageruser(username=user["sAMAccountName"][0])
                    for field, attr in settings.AUTH_LDAP_USER_ATTR_MAP.iteritems():
                        try:
                            setattr(newuser, field,
                                    user[attr][0].decode('unicode_escape').encode('iso8859-1').decode('utf8'))
                        except StandardError as e:
                            if attr == "mail":
                                print("No mail available. Skipping user.")
                                saveuser = False
                                continue
                            if attr == "sn":
                                setattr(newuser, field, user["sAMAccountName"][0])
                                continue
                            print("{0} does not have a value for the attribute {1}\n\n".format(dn, attr))
                    if saveuser:
                        newuser.save()
                        created_users += 1
            print("imported {0} users from ldap".format(created_users))

        else:
            print("You have to enable the USE_LDAP setting to use the ldap import.")