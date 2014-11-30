# -*- coding: utf-8 -*-
import ldap
from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand
import re
from users.models import Lageruser, Department, DepartmentUser
from ldap.controls import SimplePagedResultsControl
from ldap.ldapobject import LDAPObject
from datetime import date
class PagedResultsSearchObject(LDAPObject):
  page_size = 50

  def paged_search_ext_s(self,base,scope,filterstr='(objectClass=*)',attrlist=None,attrsonly=0,serverctrls=None,clientctrls=None,timeout=-1,sizelimit=0):
    """
    Behaves exactly like LDAPObject.search_ext_s() but internally uses the
    simple paged results control to retrieve search results in chunks.

    This is non-sense for really large results sets which you would like
    to process one-by-one
    """
    req_ctrl = SimplePagedResultsControl(True,size=self.page_size,cookie='')

    # Send first search request
    msgid = self.search_ext(
      *settings.LDAP_USER_SEARCH,
      serverctrls=(serverctrls or [])+[req_ctrl]
    )

    result_pages = 0
    all_results = []

    while True:
      rtype, rdata, rmsgid, rctrls = self.result3(msgid)
      all_results.extend(rdata)
      result_pages += 1
      # Extract the simple paged results response control
      pctrls = [
        c
        for c in rctrls
        if c.controlType == SimplePagedResultsControl.controlType
      ]
      if pctrls:
        if pctrls[0].cookie:
            # Copy cookie from response control to request control
            req_ctrl.cookie = pctrls[0].cookie
            msgid = self.search_ext(*settings.LDAP_USER_SEARCH, serverctrls=(serverctrls or [])+[req_ctrl])
        else:
            break
    return result_pages,all_results


class Command(BaseCommand):
    def handle(self, *args, **options):
        if settings.USE_LDAP:
            #ldap.set_option(ldap.OPT_DEBUG_LEVEL, 4095)
            l = PagedResultsSearchObject(settings.AUTH_LDAP_SERVER_URI)
            l.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
            created_users = 0
            updated_users = 0
            skipped_users = 0
            page_count, users = l.paged_search_ext_s(*settings.LDAP_USER_SEARCH)

            for dn, userdata in users:
                saveuser = False
                created = False
                try:
                    user = Lageruser.objects.get(username=userdata["sAMAccountName"][0])
                except TypeError:
                    continue
                except Exception as e:
                    saveuser = True
                    created = True
                    user = Lageruser(username=userdata["sAMAccountName"][0])
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
                        elif attr == "accountExpires":
                            if int(userdata["accountExpires"][0]) > 0:
                                expires_timestamp = (int(userdata["accountExpires"][0])/10000000)-11644473600
                                new_value = date.fromtimestamp(expires_timestamp)

                                if created and new_value < date.today():
                                    skipped_users += 1
                                    saveuser = False
                                    break

                                if user.is_active != (new_value > date.today()):
                                    user.is_active = new_value > date.today()
                                    saveuser = True
                        old_value = getattr(user, field)
                        if old_value != new_value:
                            saveuser = True
                            setattr(user, field,new_value)
                    except StandardError as e:
                        if attr == "accountExpires":
                            continue
                        if attr == "givenName" or attr == "sn":
                            skipped_users += 1
                            saveuser = False
                            break
                        if attr == "sn":
                            old_value = getattr(user, field)
                            if old_value != userdata["sAMAccountName"][0]:
                                saveuser = True
                                setattr(user, field, userdata["sAMAccountName"][0])
                                continue
                        print("{0} does not have a value for the attribute {1}".format(dn, attr))
                if saveuser:
                    user.save()
                    if user.main_department:
                        if not user.main_department in user.departments.all():
                            department_user = DepartmentUser(user=user, department=user.main_department, role="m")
                            department_user.save()
                    if created:
                        created_users += 1
                    else:
                        updated_users += 1

            print("skipped {0} users.".format(skipped_users))
            print("imported {0} new users.".format(created_users))
            print("updated {0} exisitng users.".format(updated_users))
        else:
            print("You have to enable the USE_LDAP setting to use the ldap import.")