from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import permission_required, login_required
from devices.views import *
from network.views import *
from devicetypes.views import *
from main.views import *
from api.views import *
from mail.views import *
from devicegroups.views import *
from users.views import ProfileView, UsersettingsView, UserprofileView, UserList
from rest_framework.urlpatterns import format_suffix_patterns
from . import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^$', login_required(Home.as_view()), name="home"),

    url(r'^accounts/login/$', 'users.views.login', {'template_name': 'login.html', "extra_context":{"breadcrumbs":[("", _("Login"))]}}, name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html', "extra_context":{"breadcrumbs":[("", _("Logout"))]}}, name="logout"),

    url(r'^devices/$', permission_required("devices.read_device")(DeviceList.as_view()), name="device-list"),
    url(r'^devices/page/(?P<page>[0-9]*)$', permission_required("devices.read_device")(DeviceList.as_view()), name="device-list"),
    url(r'^devices/filter/(?P<filter>[^/]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_device")(DeviceList.as_view()), name="device-list"),
    url(r'^devices/page/(?P<page>[0-9]*)/filter/(?P<filter>[^/]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_device")(DeviceList.as_view()), name="device-list"),
    url(r'^devices/add$', permission_required("devices.add_device")(DeviceCreate.as_view()), name="device-add"),
    url(r'^devices/add/template/(?P<templateid>[0-9]*)$', permission_required("devices.add_device")(DeviceCreate.as_view()), name="device-add"),
    url(r'^devices/add/copy/(?P<copyid>[0-9]*)$', permission_required("devices.add_device")(DeviceCreate.as_view()), name="device-add-copy"),
    url(r'^devices/(?P<pk>[0-9]*)$', permission_required("devices.read_device")(DeviceDetail.as_view()), name="device-detail"),
    url(r'^devices/(?P<pk>[0-9]*)/edit/$', permission_required("devices.change_device")(DeviceUpdate.as_view()), name="device-edit"),
    url(r'^devices/(?P<pk>[0-9]*)/delete/$', permission_required("devices.delete_device")(DeviceDelete.as_view()), name="device-delete"),
    url(r'^devices/(?P<pk>[0-9]*)/archive/$', permission_required("devices.change_device")(DeviceArchive.as_view()), name="device-archive"),
    url(r'^devices/(?P<pk>[0-9]*)/lend/$', permission_required("devices.lend_device")(DeviceLend.as_view()), name="device-lend"),
    url(r'^devices/(?P<pk>[0-9]*)/return/$', permission_required("devices.lend_device")(DeviceReturn.as_view()), name="device-return"),
    url(r'^devices/(?P<pk>[0-9]*)/mail/$', permission_required("devices.lend_device")(DeviceMail.as_view()), name="device-mail"),
    url(r'^devices/(?P<pk>[0-9]*)/ipaddress/$', permission_required("devices.change_device")(DeviceIpAddress.as_view()), name="device-ipaddress"),
    url(r'^devices/(?P<pk>[0-9]*)/ipaddress/(?P<ipaddress>[0-9]*)$', permission_required("devices.change_device")(DeviceIpAddressRemove.as_view()), name="device-ipaddress-remove"),
    url(r'^devices/(?P<pk>[0-9]*)/history/$', permission_required("devices.change_device")(DeviceHistoryList.as_view()), name="device-history-list"),
    url(r'^devices/(?P<pk>[0-9]*)/history/(?P<page>[0-9]*)$', permission_required("devices.change_device")(DeviceHistoryList.as_view()), name="device-history-list"),
    url(r'^devices/(?P<pk>[0-9]*)/history/revision/(?P<revision>[0-9]*)$', permission_required("devices.change_device")(DeviceHistory.as_view()), name="device-history"),
    url(r'^devices/(?P<pk>[0-9]*)/lending/$', permission_required("devices.lend_device")(DeviceLendingList.as_view()), name="device-lending-list"),
    url(r'^devices/(?P<pk>[0-9]*)/lending/(?P<page>[0-9]*)$', permission_required("devices.lend_device")(DeviceLendingList.as_view()), name="device-lending-list"),
    url(r'^devices/(?P<pk>[0-9]*)/inventoried/$', permission_required("devices.change_device")(DeviceInventoried.as_view()), name="device-inventoried"),
    url(r'^devices/(?P<pk>[0-9]*)/notes/create/$', permission_required("devices.change_device")(NoteCreate.as_view()), name="device-note-create"),

    url(r'^devices/templates/$', permission_required("devices.read_template")(TemplateList.as_view()), name="template-list"),
    url(r'^devices/templates/add$', permission_required("devices.add_template")(TemplateCreate.as_view()), name="template-add"),
    url(r'^devices/templates/(?P<pk>[0-9]*)/edit/$', permission_required("devices.change_template")(TemplateUpdate.as_view()), name="template-edit"),
    url(r'^devices/templates/(?P<pk>[0-9]*)/delete/$', permission_required("devices.delete_template")(TemplateDelete.as_view()), name="template-delete"),

    url(r'^types/$', permission_required("devicetypes.read_type")(TypeList.as_view()), name="type-list"),
    url(r'^types/(?P<page>[0-9]*)$', permission_required("devicetypes.read_type")(TypeList.as_view()), name="type-list"),
    url(r'^types/sorting/(?P<sorting>[^/]*)$', permission_required("devicetypes.read_type")(TypeList.as_view()), name="type-list"),
    url(r'^types/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devicetypes.read_type")(TypeList.as_view()), name="type-list"),
    url(r'^types/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devicetypes.read_type")(TypeList.as_view()), name="type-list"),
    url(r'^types/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devicetypes.read_type")(TypeList.as_view()), name="type-list"),
    url(r'^types/add$', permission_required("devicetypes.add_type")(TypeCreate.as_view()), name="type-add"),
    url(r'^types/edit/(?P<pk>[0-9]*)$', permission_required("devicetypes.change_type")(TypeUpdate.as_view()), name="type-edit"),
    url(r'^types/delete/(?P<pk>[0-9]*)$', permission_required("devicetypes.delete_type")(TypeDelete.as_view()), name="type-delete"),
    url(r'^types/view/(?P<pk>[0-9]*)$', permission_required("devicetypes.read_type")(TypeDetail.as_view()), name="type-detail"),
    url(r'^types/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_type")(TypeMerge.as_view()), name="type-merge"),
    url(r'^types/attribute/add$', permission_required("devicetypes.change_type")(TypeAttributeCreate.as_view()), name="typeattribute-add"),
    url(r'^types/attribute/edit/(?P<pk>[0-9]*)$', permission_required("devicetypes.change_type")(TypeAttributeUpdate.as_view()), name="typeattribute-edit"),
    url(r'^types/attribute/delete/(?P<pk>[0-9]*)$', permission_required("devicetypes.change_type")(TypeAttributeDelete.as_view()), name="typeattribute-delete"),


    url(r'^rooms/$', permission_required("devices.read_room")(RoomList.as_view()), name="room-list"),
    url(r'^rooms/(?P<page>[0-9]*)$', permission_required("devices.read_room")(RoomList.as_view()), name="room-list"),
    url(r'^rooms/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_room")(RoomList.as_view()), name="room-list"),
    url(r'^rooms/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_room")(RoomList.as_view()), name="room-list"),
    url(r'^rooms/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_room")(RoomList.as_view()), name="room-list"),
    url(r'^rooms/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_room")(RoomList.as_view()), name="room-list"),
    url(r'^rooms/add$', permission_required("devices.add_room")(RoomCreate.as_view()), name="room-add"),
    url(r'^rooms/edit/(?P<pk>[^/]*)$', permission_required("devices.read_room")(RoomUpdate.as_view()), name="room-edit"),
    url(r'^rooms/delete/(?P<pk>[^/]*)$', permission_required("devices.delete_room")(RoomDelete.as_view()), name="room-delete"),
    url(r'^rooms/view/(?P<pk>[^/]*)$', permission_required("devices.read_room")(RoomDetail.as_view()), name="room-detail"),
    url(r'^rooms/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_room")(RoomMerge.as_view()), name="room-merge"),

    url(r'^buildings/$', permission_required("devices.read_building")(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/(?P<page>[0-9]*)$', permission_required("devices.read_building")(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_building")(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_building")(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_building")(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_building")(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/add$', permission_required("devices.add_building")(BuildingCreate.as_view()), name="building-add"),
    url(r'^buildings/edit/(?P<pk>[^/]*)$', permission_required("devices.change_building")(BuildingUpdate.as_view()), name="building-edit"),
    url(r'^buildings/delete/(?P<pk>[^/]*)$', permission_required("devices.delete_building")(BuildingDelete.as_view()), name="building-delete"),
    url(r'^buildings/view/(?P<pk>[^/]*)$', permission_required("devices.read_building")(BuildingDetail.as_view()), name="building-detail"),
    url(r'^buildings/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_building")(BuildingMerge.as_view()), name="building-merge"),

    url(r'^manufacturers/$', permission_required("devices.read_manufacturer")(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/page/(?P<page>[0-9]*)$', permission_required("devices.read_manufacturer")(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_manufacturer")(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devices.read_manufacturer")(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_manufacturer")(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_manufacturer")(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/add$', permission_required("devices.add_manufacturer")(ManufacturerCreate.as_view()), name="manufacturer-add"),
    url(r'^manufacturers/edit/(?P<pk>[^/]*)$', permission_required("devices.change_manufacturer")(ManufacturerUpdate.as_view()), name="manufacturer-edit"),
    url(r'^manufacturers/delete/(?P<pk>[^/]*)$', permission_required("devices.delete_manufacturer")(ManufacturerDelete.as_view()), name="manufacturer-delete"),
    url(r'^manufacturers/view/(?P<pk>[^/]*)$', permission_required("devices.read_manufacturer")(ManufacturerDetail.as_view()), name="manufacturer-detail"),
    url(r'^manufacturers/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', permission_required("devices.change_manufacturer")(ManufacturerMerge.as_view()), name="manufacturer-merge"),

    url(r'^mails/$', permission_required("mail.read_mailtemplate")(MailList.as_view()), name="mail-list"),
    url(r'^mails/(?P<page>[0-9]*)$', permission_required("mail.read_mailtemplate")(MailList.as_view()), name="mail-list"),
    url(r'^mails/add$', permission_required("mail.add_mailtemplate")(MailCreate.as_view()), name="mail-add"),
    url(r'^mails/edit/(?P<pk>[^/]*)$', permission_required("mail.change_mailtemplate")(MailUpdate.as_view()), name="mail-edit"),
    url(r'^mails/view/(?P<pk>[^/]*)$', permission_required("mail.read_mailtemplate")(MailDetail.as_view()), name="mail-detail"),
    url(r'^mails/delete/(?P<pk>[^/]*)$', permission_required("mail.delete_mailtemplate")(MailDelete.as_view()), name="mail-delete"),

    url(r'^devicegroups/$', permission_required("devicegroups.read_devicegroup")(DevicegroupList.as_view()), name="devicegroup-list"),
    url(r'^devicegroups/(?P<page>[0-9]*)$', permission_required("devicegroups.read_devicegroup")(DevicegroupList.as_view()), name="devicegroup-list"),
    url(r'^devicegroups/sorting/(?P<sorting>[^/]*)$', permission_required("devicegroups.read_devicegroup")(DevicegroupList.as_view()), name="devicegroup-list"),
    url(r'^devicegroups/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)$', permission_required("devicegroups.read_devicegroup")(DevicegroupList.as_view()), name="devicegroup-list"),
    url(r'^devicegroups/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devicegroups.read_devicegroup")(DevicegroupList.as_view()), name="devicegroup-list"),
    url(r'^devicegroups/page/(?P<page>[0-9]*)/sorting/(?P<sorting>[^/]*)/filter/(?P<filter>[^/]*)$', permission_required("devicegroups.read_devicegroup")(DevicegroupList.as_view()), name="devicegroup-list"),
    url(r'^devicegroups/add$', permission_required("devicegroups.add_devicegroup")(DevicegroupCreate.as_view()), name="devicegroup-add"),
    url(r'^devicegroups/edit/(?P<pk>[^/]*)$', permission_required("devicegroups.change_devicegroup")(DevicegroupUpdate.as_view()), name="devicegroup-edit"),
    url(r'^devicegroups/view/(?P<pk>[^/]*)$', permission_required("devicegroups.read_devicegroup")(DevicegroupDetail.as_view()), name="devicegroup-detail"),
    url(r'^devicegroups/delete/(?P<pk>[^/]*)$', permission_required("devicegroups.delete_devicegroup")(DevicegroupDelete.as_view()), name="devicegroup-delete"),


    url(r'^ipaddresses/$', permission_required("network.read_ipaddress")(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/page/(?P<page>[0-9]*)$', permission_required("network.read_ipaddress")(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/page/(?P<page>[0-9]*)/filter/(?P<filter>[^/]*)$', permission_required("network.read_ipaddress")(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/add$', permission_required("network.add_ipaddress")(IpAddressCreate.as_view()), name="ipaddress-add"),
    url(r'^ipaddresses/edit/(?P<pk>[^/]*)$', permission_required("network.change_ipaddress")(IpAddressUpdate.as_view()), name="ipaddress-edit"),
    url(r'^ipaddresses/delete/(?P<pk>[^/]*)$', permission_required("network.delete_ipaddress")(IpAddressDelete.as_view()), name="ipaddress-delete"),
    url(r'^ipaddresses/view/(?P<pk>[^/]*)$', permission_required("network.read_ipaddress")(IpAddressDetail.as_view()), name="ipaddress-detail"),

    url(r'^users/$', permission_required("users.read_user")(UserList.as_view()), name="user-list"),
    url(r'^users/(?P<page>[0-9]*)$', permission_required("users.read_user")(UserList.as_view()), name="user-list"),
    url(r'^users/filter/(?P<filter>[^/]*)$', permission_required("users.read_user")(UserList.as_view()), name="user-list"),
    url(r'^users/page/(?P<page>[0-9]*)/filter/(?P<filter>[^/]*)$', permission_required("devices.read_user")(UserList.as_view()), name="user-list"),
    url(r'^users/view/(?P<pk>[0-9]*)$', permission_required("users.read_user")(ProfileView.as_view()), name="userprofile"),
    url(r'^profile', login_required(UserprofileView.as_view()), name="userprofile"),
    url(r'^settings', login_required(UsersettingsView.as_view()), name="usersettings"),

    url(r'^globalhistory/$', permission_required("devices.change_device")(Globalhistory.as_view()), name="globalhistory"),
    url(r'^globalhistory/(?P<page>[0-9]*)$', permission_required("devices.change_device")(Globalhistory.as_view()), name="globalhistory"),

    url(r'^search/$', permission_required("devices.read_device")(Search.as_view()), name="search"),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)

urlpatterns += format_suffix_patterns(patterns('',
    url(r'^api/$', api_root),
    url(r'^api/devices/$', DeviceApiList.as_view(), name='device-api-list'),
    url(r'^api/devices/create/$', DeviceApiCreate.as_view(), name='device-api-create'),
    url(r'^api/devices/(?P<pk>\d+)/$', DeviceApiDetail.as_view(), name='device-api-detail'),
    
    url(r'^api/manufacturers/$', ManufacturerApiList.as_view(), name='manufacturer-api-list'),
    url(r'^api/manufacturers/create/$', ManufacturerApiCreate.as_view(), name='manufacturer-api-create'),
    url(r'^api/manufacturers/(?P<pk>\d+)/$', ManufacturerApiDetail.as_view(), name='manufacturer-api-detail'),
    
    url(r'^api/rooms/$', RoomApiList.as_view(), name='room-api-list'),
    url(r'^api/rooms/create/$', RoomApiCreate.as_view(), name='room-api-create'),
    url(r'^api/rooms/(?P<pk>\d+)/$', RoomApiDetail.as_view(), name='room-api-detail'),
    
    url(r'^api/types/$', TypeApiList.as_view(), name='type-api-list'),
    url(r'^api/types/create/$', TypeApiCreate.as_view(), name='type-api-create'),
    url(r'^api/types/(?P<pk>\d+)/$', TypeApiDetail.as_view(), name='type-api-detail'),
    
    url(r'^api/buildings/$', BuildingApiList.as_view(), name='building-api-list'),
    url(r'^api/buildings/create/$', BuildingApiCreate.as_view(), name='building-api-create'),
    url(r'^api/buildings/(?P<pk>\d+)/$', BuildingApiDetail.as_view(), name='building-api-detail'),
    
    url(r'^api/templates/$', TemplateApiList.as_view(), name='template-api-list'),
    url(r'^api/templates/create/$', TemplateApiCreate.as_view(), name='template-api-create'),
    url(r'^api/templates/(?P<pk>\d+)/$', TemplateApiDetail.as_view(), name='template-api-detail'),
    
    url(r'^api/ipaddresses/$', IpAddressApiList.as_view(), name='ipaddress-api-list'),
    url(r'^api/ipaddresses/create/$', IpAddressApiCreate.as_view(), name='ipaddress-api-create'),
    url(r'^api/ipaddresses/(?P<pk>\d+)/$', IpAddressApiDetail.as_view(), name='ipaddress-api-detail'),
    
    url(r'^api/users/$', UserApiList.as_view(), name='user-api-list'),
    url(r'^api/users/(?P<pk>\d+)/$', UserApiDetail.as_view(), name='user-api-detail'),

    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
), allowed=["json", "html"])

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))