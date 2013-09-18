from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import permission_required, login_required
from devices.views import *
from network.views import *
from devicetypes.views import *
from main.views import *
from api.views import *
from mail.views import *
from users.views import ProfileView, UsersettingsView, UserprofileView
from rest_framework.urlpatterns import format_suffix_patterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name="home"),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html', "extra_context":{"breadcrumbs":[("", _("Login"))]}}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html', "extra_context":{"breadcrumbs":[("", _("Logout"))]}}),

    url(r'^devices/$', permission_required("devices.read_device", raise_exception=True)(DeviceList.as_view()), name="device-list"),
    url(r'^devices/page/(?P<page>[0-9]*)$', permission_required("devices.read_device", raise_exception=True)(DeviceList.as_view()), name="device-list"),
    url(r'^devices/filter/(?P<filter>.*)$', permission_required("devices.read_device", raise_exception=True)(DeviceList.as_view()), name="device-list-filtered"),
    url(r'^devices/page/(?P<page>[0-9]*)/filter/(?P<filter>.*)$', permission_required("devices.read_device", raise_exception=True)(DeviceList.as_view()), name="device-list-filtered"),
    url(r'^devices/globalhistory/$', permission_required("devices.change_device", raise_exception=True)(DeviceGlobalhistory.as_view()), name="device-globalhistory"),
    url(r'^devices/globalhistory/(?P<page>[0-9]*)$', permission_required("devices.change_device", raise_exception=True)(DeviceGlobalhistory.as_view()), name="device-globalhistory"),
    url(r'^devices/add$', permission_required("devices.create_device", raise_exception=True)(DeviceCreate.as_view()), name="device-add"),
    url(r'^devices/add/template/(?P<templateid>[0-9]*)$', permission_required("devices.create_device", raise_exception=True)(DeviceCreate.as_view()), name="device-add"),
    url(r'^devices/add/copy/(?P<copyid>[0-9]*)$', permission_required("devices.create_device", raise_exception=True)(DeviceCreate.as_view()), name="device-add-copy"),
    url(r'^devices/(?P<pk>[0-9]*)$', permission_required("devices.read_device", raise_exception=True)(DeviceDetail.as_view()), name="device-detail"),
    url(r'^devices/(?P<pk>[0-9]*)/edit/$', permission_required("devices.change_device", raise_exception=True)(DeviceUpdate.as_view()), name="device-edit"),
    url(r'^devices/(?P<pk>[0-9]*)/delete/$', permission_required("devices.delete_device", raise_exception=True)(DeviceDelete.as_view()), name="device-delete"),
    url(r'^devices/(?P<pk>[0-9]*)/archive/$', permission_required("devices.change_device", raise_exception=True)(DeviceArchive.as_view()), name="device-archive"),
    url(r'^devices/(?P<pk>[0-9]*)/lend/$', permission_required("devices.lend_device", raise_exception=True)(DeviceLend.as_view()), name="device-lend"),
    url(r'^devices/(?P<pk>[0-9]*)/return/$', permission_required("devices.lend_device", raise_exception=True)(DeviceReturn.as_view()), name="device-return"),
    url(r'^devices/(?P<pk>[0-9]*)/mail/$', permission_required("devices.lend_device", raise_exception=True)(DeviceMail.as_view()), name="device-mail"),
    url(r'^devices/(?P<pk>[0-9]*)/ipaddress/$', permission_required("devices.change_device", raise_exception=True)(DeviceIpAddress.as_view()), name="device-ipaddress"),
    url(r'^devices/(?P<pk>[0-9]*)/ipaddress/(?P<ipaddress>[0-9]*)$', permission_required("devices.change_device", raise_exception=True)(DeviceIpAddressRemove.as_view()), name="device-ipaddress-remove"),
    url(r'^devices/(?P<pk>[0-9]*)/history/$', permission_required("devices.change_device", raise_exception=True)(DeviceHistoryList.as_view()), name="device-history-list"),
    url(r'^devices/(?P<pk>[0-9]*)/history/(?P<revision>[0-9]*)$', permission_required("devices.change_device", raise_exception=True)(DeviceHistory.as_view()), name="device-history"),

     url(r'^devices/templates/$', permission_required("devices.read_template", raise_exception=True)(TemplateList.as_view()), name="template-list"),
    url(r'^devices/templates/add$', permission_required("devices.create_template", raise_exception=True)(TemplateCreate.as_view()), name="template-add"),
    url(r'^devices/templates/(?P<pk>[0-9]*)/edit/$', permission_required("devices.change_template", raise_exception=True)(TemplateUpdate.as_view()), name="template-edit"),
    url(r'^devices/templates/(?P<pk>[0-9]*)/delete/$', permission_required("devices.delete_template", raise_exception=True)(TemplateDelete.as_view()), name="template-delete"),

    url(r'^types/$', permission_required("devicetypes.read_type", raise_exception=True)(TypeList.as_view()), name="type-list"),
    url(r'^types/(?P<page>[0-9]*)$', permission_required("devicetypes.read_type", raise_exception=True)(TypeList.as_view()), name="type-list"),
    url(r'^types/add$', permission_required("devicetypes.create_type", raise_exception=True)(TypeCreate.as_view()), name="type-add"),
    url(r'^types/edit/(?P<pk>[0-9]*)$', permission_required("devicetypes.change_type", raise_exception=True)(TypeUpdate.as_view()), name="type-edit"),
    url(r'^types/delete/(?P<pk>[0-9]*)$', permission_required("devicetypes.delete_type", raise_exception=True)(TypeDelete.as_view()), name="type-delete"),
    url(r'^types/view/(?P<pk>[0-9]*)$', permission_required("devicetypes.read_type", raise_exception=True)(TypeDetail.as_view()), name="type-detail"),
    url(r'^types/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_type", raise_exception=True)(TypeMerge.as_view()), name="type-merge"),
    url(r'^types/attribute/add$', permission_required("devicetypes.change_type", raise_exception=True)(TypeAttributeCreate.as_view()), name="typeattribute-add"),
    url(r'^types/attribute/edit/(?P<pk>[0-9]*)$', permission_required("devicetypes.change_type", raise_exception=True)(TypeAttributeUpdate.as_view()), name="typeattribute-edit"),
    url(r'^types/attribute/delete/(?P<pk>[0-9]*)$', permission_required("devicetypes.change_type", raise_exception=True)(TypeAttributeDelete.as_view()), name="typeattribute-delete"),


    url(r'^rooms/$', permission_required("devices.read_room", raise_exception=True)(RoomList.as_view()), name="room-list"),
    url(r'^rooms/(?P<page>[0-9]*)$', permission_required("devices.read_room", raise_exception=True)(RoomList.as_view()), name="room-list"),
    url(r'^rooms/add$', permission_required("devices.create_room", raise_exception=True)(RoomCreate.as_view()), name="room-add"),
    url(r'^rooms/edit/(?P<pk>.*)$', permission_required("devices.read_room", raise_exception=True)(RoomUpdate.as_view()), name="room-edit"),
    url(r'^rooms/delete/(?P<pk>.*)$', permission_required("devices.delete_room", raise_exception=True)(RoomDelete.as_view()), name="room-delete"),
    url(r'^rooms/view/(?P<pk>.*)$', permission_required("devices.read_room", raise_exception=True)(RoomDetail.as_view()), name="room-detail"),
    url(r'^rooms/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_room", raise_exception=True)(RoomMerge.as_view()), name="room-merge"),

    url(r'^buildings/$', permission_required("devices.read_building", raise_exception=True)(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/(?P<page>[0-9]*)$', permission_required("devices.read_building", raise_exception=True)(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/add$', permission_required("devices.create_building", raise_exception=True)(BuildingCreate.as_view()), name="building-add"),
    url(r'^buildings/edit/(?P<pk>.*)$', permission_required("devices.change_building", raise_exception=True)(BuildingUpdate.as_view()), name="building-edit"),
    url(r'^buildings/delete/(?P<pk>.*)$', permission_required("devices.delete_building", raise_exception=True)(BuildingDelete.as_view()), name="building-delete"),
    url(r'^buildings/view/(?P<pk>.*)$', permission_required("devices.read_building", raise_exception=True)(BuildingDetail.as_view()), name="building-detail"),
    url(r'^buildings/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_building", raise_exception=True)(BuildingMerge.as_view()), name="building-merge"),

    url(r'^manufacturers/$', permission_required("devices.read_manufacturer", raise_exception=True)(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/(?P<page>[0-9]*)$', permission_required("devices.read_manufacturer", raise_exception=True)(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/add$', permission_required("devices.create_manufacturer", raise_exception=True)(ManufacturerCreate.as_view()), name="manufacturer-add"),
    url(r'^manufacturers/edit/(?P<pk>.*)$', permission_required("devices.change_manufacturer", raise_exception=True)(ManufacturerUpdate.as_view()), name="manufacturer-edit"),
    url(r'^manufacturers/delete/(?P<pk>.*)$', permission_required("devices.delete_manufacturer", raise_exception=True)(ManufacturerDelete.as_view()), name="manufacturer-delete"),
    url(r'^manufacturers/view/(?P<pk>.*)$', permission_required("devices.read_manufacturer", raise_exception=True)(ManufacturerDetail.as_view()), name="manufacturer-detail"),
    url(r'^manufacturers/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_manufacturer", raise_exception=True)(ManufacturerMerge.as_view()), name="manufacturer-merge"),

    url(r'^mails/$', permission_required("mail.read_mailtemplate", raise_exception=True)(MailList.as_view()), name="mail-list"),
    url(r'^mails/(?P<page>[0-9]*)$', permission_required("mail.read_mailtemplate", raise_exception=True)(MailList.as_view()), name="mail-list"),
    url(r'^mails/add$', permission_required("mail.create_mailtemplate", raise_exception=True)(MailCreate.as_view()), name="mail-add"),
    url(r'^mails/edit/(?P<pk>.*)$', permission_required("mail.change_mailtemplate", raise_exception=True)(MailUpdate.as_view()), name="mail-edit"),
    url(r'^mails/view/(?P<pk>.*)$', permission_required("mail.read_mailtemplate", raise_exception=True)(MailDetail.as_view()), name="mail-detail"),
    url(r'^mails/delete/(?P<pk>.*)$', permission_required("mail.delete_mailtemplate", raise_exception=True)(MailDelete.as_view()), name="mail-delete"),

    url(r'^ipaddresses/$', permission_required("network.read_ipaddress", raise_exception=True)(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/page/(?P<page>[0-9]*)$', permission_required("network.read_ipaddress", raise_exception=True)(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/filter/(?P<filter>.*)$', permission_required("network.read_ipaddress", raise_exception=True)(IpAddressList.as_view()), name="ipaddress-list-filtered"),
    url(r'^ipaddresses/page/(?P<page>[0-9]*)/filter/(?P<filter>.*)$', permission_required("network.read_ipaddress", raise_exception=True)(IpAddressList.as_view()), name="ipaddress-list-filtered"),
    url(r'^ipaddresses/add$', permission_required("network.create_ipaddress", raise_exception=True)(IpAddressCreate.as_view()), name="ipaddress-add"),
    url(r'^ipaddresses/edit/(?P<pk>.*)$', permission_required("network.change_ipaddress", raise_exception=True)(IpAddressUpdate.as_view()), name="ipaddress-edit"),
    url(r'^ipaddresses/delete/(?P<pk>.*)$', permission_required("network.delete_ipaddress", raise_exception=True)(IpAddressDelete.as_view()), name="ipaddress-delete"),
    url(r'^ipaddresses/view/(?P<pk>.*)$', permission_required("network.read_ipaddress", raise_exception=True)(IpAddressDetail.as_view()), name="ipaddress-detail"),

    url(r'^users/(?P<pk>[0-9]*)$', permission_required("devices.read_user", raise_exception=True)(ProfileView.as_view()), name="userprofile"),
    url(r'^profile', login_required(UserprofileView.as_view()), name="userprofile"),
    url(r'^settings', login_required(UsersettingsView.as_view()), name="usersettings"),

    url(r'^search/$', permission_required("devices.read_device", raise_exception=True)(Search.as_view()), name="search"),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += format_suffix_patterns(patterns('',
    url(r'^api/$', api_root),
    url(r'^api/devices/$', DeviceApiList.as_view(), name='device-api-list'),
    url(r'^api/devices/(?P<pk>\d+)/$', DeviceApiDetail.as_view(), name='device-api-detail'),
    url(r'^api/manufacturers/$', ManufacturerApiList.as_view(), name='manufacturer-api-list'),
    url(r'^api/manufacturers/(?P<pk>\d+)/$', ManufacturerApiDetail.as_view(), name='manufacturer-api-detail'),
    url(r'^api/rooms/$', RoomApiList.as_view(), name='room-api-list'),
    url(r'^api/rooms/(?P<pk>\d+)/$', RoomApiDetail.as_view(), name='room-api-detail'),
    url(r'^api/types/$', TypeApiList.as_view(), name='type-api-list'),
    url(r'^api/types/(?P<pk>\d+)/$', TypeApiDetail.as_view(), name='type-api-detail'),
    url(r'^api/types/attributes/(?P<pk>\d+)/$', TypeAttributeApiDetail.as_view(), name='typeattribute-api-detail'),
    url(r'^api/buildings/$', BuildingApiList.as_view(), name='building-api-list'),
    url(r'^api/buildings/(?P<pk>\d+)/$', BuildingApiDetail.as_view(), name='building-api-detail'),
    url(r'^api/templates/$', TemplateApiList.as_view(), name='template-api-list'),
    url(r'^api/templates/(?P<pk>\d+)/$', TemplateApiDetail.as_view(), name='template-api-detail'),
    url(r'^api/ipaddresses/$', IpAddressApiList.as_view(), name='ipaddress-api-list'),
    url(r'^api/ipaddresses/(?P<pk>\d+)/$', IpAddressApiDetail.as_view(), name='ipaddress-api-detail'),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
), allowed=["json", "html"])