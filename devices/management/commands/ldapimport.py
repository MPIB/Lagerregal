import re
from datetime import date

from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand

from ldap.controls import SimplePagedResultsControl
from ldap.ldapobject import LDAPObject

from Lagerregal import utils
from users.models import Department
from users.models import DepartmentUser
from users.models import Lageruser


class PagedResultsSearchObject(LDAPObject):
    page_size = 50

    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None, attrsonly=0, serverctrls=None, clientctrls=None, timeout=-1, sizelimit=0):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.

        This is non-sense for really large results sets which you would like
        to process one-by-one
        """
        req_ctrl = SimplePagedResultsControl(True, size=self.page_size, cookie='')

        # Send first search request
        msgid = self.search_ext(
            *settings.LDAP_USER_SEARCH,
            serverctrls=(serverctrls or []) + [req_ctrl]
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
                    msgid = self.search_ext(*settings.LDAP_USER_SEARCH, serverctrls=(serverctrls or []) + [req_ctrl])
                else:
                    break
        return result_pages, all_results


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.USE_LDAP:
            print("You have to enable the USE_LDAP setting to use the ldap import.")
            return
        # ldap.set_option(ldap.OPT_DEBUG_LEVEL, 4095)
        search = PagedResultsSearchObject(settings.AUTH_LDAP_SERVER_URI)
        search.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        created_users = 0
        updated_users = 0
        skipped_users = 0
        page_count, users = search.paged_search_ext_s(*settings.LDAP_USER_SEARCH)
        attr_map = settings.AUTH_LDAP_USER_ATTR_MAP
        attr_map.update({'main_department': settings.AUTH_LDAP_DEPARTMENT_FIELD})

        for dn, userdata in users:
            # paged results contains weird ldap references..
            if not isinstance(userdata, dict):
                print(userdata)
                continue
            username = userdata['sAMAccountName'][0].decode('utf-8')
            saveuser = False
            created = False
            changes = {}
            try:
                user = Lageruser.objects.get(username=username)
            except:
                saveuser = True
                created = True
                user = Lageruser(username=username)
            for field, attr in attr_map.items():
                try:
                    old_value = getattr(user, field)
                    new_value = userdata[attr][0].decode('utf-8')
                    if attr == settings.AUTH_LDAP_DEPARTMENT_FIELD:
                        try:
                            department_name = re.findall(settings.AUTH_LDAP_DEPARTMENT_REGEX, new_value)[-1]
                            new_value = Department.objects.get(name=department_name)
                        except Department.DoesNotExist:
                            new_value = Department(name=department_name)
                            new_value.save()
                        except IndexError:
                            skipped_users += 1
                            saveuser = False
                            break
                    elif attr == "accountExpires":
                        expired = False
                        if int(userdata['accountExpires'][0].decode('utf-8')) == 0:
                            new_value = None
                        else:
                            new_value = utils.convert_ad_accountexpires(int(userdata['accountExpires'][0]))
                            if new_value is not None:
                                expired = new_value < date.today()

                        if created and expired:
                            skipped_users += 1
                            saveuser = False
                            break

                        if user.is_active == expired:
                            user.is_active = not expired
                            saveuser = True

                    if old_value != new_value and (created or attr not in settings.AUTH_LDAP_ATTR_NOSYNC):
                        saveuser = True
                        setattr(user, field, new_value)
                        changes[field] = (old_value, new_value)
                except:
                    if attr == "accountExpires":
                        continue
                    if attr == "givenName" or attr == "sn":
                        skipped_users += 1
                        saveuser = False
                        break
                    if attr == "sn":
                        old_value = getattr(user, field)
                        if old_value != username:
                            saveuser = True
                            setattr(user, field, username)
                            continue
                    if attr == "mail":
                        # userPrincipalName *might* contain non-ascii
                        # characters but is a sane fallback for when "mail"
                        # does not exist
                        old_value = getattr(user, field)
                        try:
                            new_value = userdata["userPrincipalName"][0].decode('ascii')
                            if old_value != new_value:
                                saveuser = True
                                setattr(user, field, new_value)
                            continue
                        except Exception:
                            pass

                    print("{0} does not have a value for the attribute {1}".format(dn, attr))
            if saveuser:
                if user.is_active == expired:
                    if expired:
                        print("{0} has expired".format(dn))
                    else:
                        print("{0} has been reactivated".format(dn))
                for field, (old_value, new_value) in changes.items():
                    print('{0} changed {1} from {2} to {3}'.format(dn, field, old_value, new_value))
                user.save()
                if user.main_department:
                    if user.main_department not in user.departments.all():
                        department_user = DepartmentUser(user=user, department=user.main_department, role="m")
                        department_user.save()
                if created:
                    created_users += 1
                else:
                    updated_users += 1

        if created_users > 0 or updated_users > 0:
            print("imported {0} new users.".format(created_users))
            print("updated {0} exisitng users.".format(updated_users))
