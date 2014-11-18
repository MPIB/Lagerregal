# -*- coding: utf-8 -*-
import ldap
from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand
import re
from users.models import Lageruser, Department, DepartmentUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.USE_LDAP:
            #ldap.set_option(ldap.OPT_DEBUG_LEVEL, 4095)
            l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
            l.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
            created_users = 0
            updated_users = 0
            skipped_users = 0
            for directory in settings.LDAP_USER_SEARCH_DIRECTORIES:
                users = l.search_ext_s(directory, *settings.LDAP_USER_SEARCH, sizelimit=1000)
                print("Found {0} users in LDAP directory.".format(len(users)))

                for dn, userdata in users:
                    saveuser = False
                    created = False
                    try:
                        user = Lageruser.objects.get(username=userdata["sAMAccountName"][0])
                    except Exception as e:
                        saveuser = True
                        created = True
                        user = Lageruser(username=userdata["sAMAccountName"][0])
                        user.save()
                    for field, attr in settings.AUTH_LDAP_USER_ATTR_MAP.iteritems():
                        try:
                            new_value = userdata[attr][0].decode('unicode_escape').encode('iso8859-1').decode('utf8')
                            if attr == settings.AUTH_LDAP_DEPARTMENT_FIELD:
                                department_name = re.findall(settings.AUTH_LDAP_DEPARTMENT_REGEX, new_value)[-1]
                                try:
                                    new_value = Department.objects.get(name=department_name)
                                except Department.DoesNotExist as e:
                                    new_value = Department(name=department_name)
                                    new_value.save()
                                if not new_value in user.departments.all():
                                    department_user = DepartmentUser(user=user, department=new_value, role="m")
                                    department_user.save()
                            old_value = getattr(user, field)
                            if old_value != new_value:
                                saveuser = True
                                setattr(user, field,new_value)
                        except StandardError as e:
                            if attr == "mail":
                                skipped_users += 1
                                saveuser = False
                                continue
                            if attr == "sn":
                                old_value = getattr(user, field)
                                if old_value != userdata["sAMAccountName"][0]:
                                    saveuser = True
                                    setattr(user, field, userdata["sAMAccountName"][0])
                                    continue
                            print("{0} does not have a value for the attribute {1}\n\n".format(dn, attr))
                    if saveuser:
                        user.save()
                        if created:
                            created_users += 1
                        else:
                            updated_users += 1
            print("skipped {0} users.".format(skipped_users))
            print("imported {0} new users.".format(created_users))
            print("updated {0} exisitng users.".format(updated_users))

        else:
            print("You have to enable the USE_LDAP setting to use the ldap import.")