from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from devices.views import *
from network.views import *
from users.views import ProfileView
from django.views.generic import TemplateView
from rest_framework.urlpatterns import format_suffix_patterns
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^$', Home.as_view(), name="home"),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html', }),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),

    url(r'^devices/$', login_required(DeviceList.as_view()), name="device-list"),
    url(r'^devices/page/(?P<page>[0-9]*)$', login_required(DeviceList.as_view()), name="device-list"),
    url(r'^devices/filter/(?P<filter>.*)$', login_required(DeviceList.as_view()), name="device-list-filtered"),
    url(r'^devices/page/(?P<page>[0-9]*)/filter/(?P<filter>.*)$', login_required(DeviceList.as_view()), name="device-list-filtered"),
    url(r'^devices/globalhistory/$', login_required(DeviceGlobalhistory.as_view()), name="device-globalhistory"),
    url(r'^devices/globalhistory/(?P<page>[0-9]*)$', login_required(DeviceGlobalhistory.as_view()), name="device-globalhistory"),
    url(r'^devices/add$', login_required(DeviceCreate.as_view()), name="device-add"),
    url(r'^devices/add/template/(?P<templateid>[0-9]*)$', login_required(DeviceCreate.as_view()), name="device-add"),
    url(r'^devices/add/copy/(?P<copyid>[0-9]*)$', login_required(DeviceCreate.as_view()), name="device-add-copy"),
    url(r'^devices/(?P<pk>[0-9]*)$', login_required(DeviceDetail.as_view()), name="device-detail"),
    url(r'^devices/(?P<pk>[0-9]*)/edit/$', login_required(DeviceUpdate.as_view()), name="device-edit"),
    url(r'^devices/(?P<pk>[0-9]*)/delete/$', login_required(DeviceDelete.as_view()), name="device-delete"),
    url(r'^devices/(?P<pk>[0-9]*)/archive/$', login_required(DeviceArchive.as_view()), name="device-archive"),
    url(r'^devices/(?P<pk>[0-9]*)/lend/$', login_required(DeviceLend.as_view()), name="device-lend"),
    url(r'^devices/(?P<pk>[0-9]*)/return/$', login_required(DeviceReturn.as_view()), name="device-return"),
    url(r'^devices/(?P<pk>[0-9]*)/ipaddress/$', login_required(DeviceIpAddress.as_view()), name="device-ipaddress"),
    url(r'^devices/(?P<pk>[0-9]*)/ipaddress/(?P<ipaddress>[0-9]*)$', login_required(DeviceIpAddressRemove.as_view()), name="device-ipaddress-remove"),
    url(r'^devices/(?P<pk>[0-9]*)/history/$', login_required(DeviceHistoryList.as_view()), name="device-history-list"),
    url(r'^devices/(?P<pk>[0-9]*)/history/(?P<revision>[0-9]*)$', login_required(DeviceHistory.as_view()), name="device-history"),

     url(r'^templates/$', login_required(TemplateList.as_view()), name="template-list"),
    url(r'^templates/add$', login_required(TemplateCreate.as_view()), name="template-add"),
    url(r'^templates/(?P<pk>[0-9]*)/edit/$', login_required(TemplateUpdate.as_view()), name="template-edit"),
    url(r'^templates/(?P<pk>[0-9]*)/delete/$', login_required(TemplateDelete.as_view()), name="template-delete"),

    url(r'^types/$', login_required(TypeList.as_view()), name="type-list"),
    url(r'^types/(?P<page>[0-9]*)$', login_required(TypeList.as_view()), name="type-list"),
    url(r'^types/add$', login_required(TypeCreate.as_view()), name="type-add"),
    url(r'^types/edit/(?P<pk>[0-9]*)$', login_required(TypeUpdate.as_view()), name="type-edit"),
    url(r'^types/delete/(?P<pk>[0-9]*)$', login_required(TypeDelete.as_view()), name="type-delete"),
    url(r'^types/view/(?P<pk>[0-9]*)$', login_required(TypeDetail.as_view()), name="type-detail"),
    url(r'^types/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', login_required(TypeMerge.as_view()), name="type-merge"),

    url(r'^rooms/$', login_required(RoomList.as_view()), name="room-list"),
    url(r'^rooms/(?P<page>[0-9]*)$', login_required(RoomList.as_view()), name="room-list"),
    url(r'^rooms/add$', login_required(RoomCreate.as_view()), name="room-add"),
    url(r'^rooms/edit/(?P<pk>.*)$', login_required(RoomUpdate.as_view()), name="room-edit"),
    url(r'^rooms/delete/(?P<pk>.*)$', login_required(RoomDelete.as_view()), name="room-delete"),
    url(r'^rooms/view/(?P<pk>.*)$', login_required(RoomDetail.as_view()), name="room-detail"),
    url(r'^rooms/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', login_required(RoomMerge.as_view()), name="room-merge"),

    url(r'^buildings/$', login_required(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/(?P<page>[0-9]*)$', login_required(BuildingList.as_view()), name="building-list"),
    url(r'^buildings/add$', login_required(BuildingCreate.as_view()), name="building-add"),
    url(r'^buildings/edit/(?P<pk>.*)$', login_required(BuildingUpdate.as_view()), name="building-edit"),
    url(r'^buildings/delete/(?P<pk>.*)$', login_required(BuildingDelete.as_view()), name="building-delete"),
    url(r'^buildings/view/(?P<pk>.*)$', login_required(BuildingDetail.as_view()), name="building-detail"),
    url(r'^buildings/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', login_required(BuildingMerge.as_view()), name="building-merge"),

    url(r'^manufacturers/$', login_required(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/(?P<page>[0-9]*)$', login_required(ManufacturerList.as_view()), name="manufacturer-list"),
    url(r'^manufacturers/add$', login_required(ManufacturerCreate.as_view()), name="manufacturer-add"),
    url(r'^manufacturers/edit/(?P<pk>.*)$', login_required(ManufacturerUpdate.as_view()), name="manufacturer-edit"),
    url(r'^manufacturers/delete/(?P<pk>.*)$', login_required(ManufacturerDelete.as_view()), name="manufacturer-delete"),
    url(r'^manufacturers/view/(?P<pk>.*)$', login_required(ManufacturerDetail.as_view()), name="manufacturer-detail"),
    url(r'^manufacturers/merge/(?P<oldpk>[0-9]*)/(?P<newpk>[0-9]*)$', login_required(ManufacturerMerge.as_view()), name="manufacturer-merge"),

    url(r'^ipaddresses/$', login_required(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/(?P<page>[0-9]*)$', login_required(IpAddressList.as_view()), name="ipaddress-list"),
    url(r'^ipaddresses/add$', login_required(IpAddressCreate.as_view()), name="ipaddress-add"),
    url(r'^ipaddresses/edit/(?P<pk>.*)$', login_required(IpAddressUpdate.as_view()), name="ipaddress-edit"),
    url(r'^ipaddresses/delete/(?P<pk>.*)$', login_required(IpAddressDelete.as_view()), name="ipaddress-delete"),
    url(r'^ipaddresses/view/(?P<pk>.*)$', login_required(IpAddressDetail.as_view()), name="ipaddress-detail"),

    url(r'^users/(?P<pk>[0-9]*)$', login_required(ProfileView.as_view()), name="userprofile"),

    url(r'^search/$', login_required(Search.as_view()), name="search"),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
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
    url(r'^api/buildings/$', BuildingApiList.as_view(), name='building-api-list'),
    url(r'^api/buildings/(?P<pk>\d+)/$', BuildingApiDetail.as_view(), name='building-api-detail'),
    url(r'^api/templates/$', TemplateApiList.as_view(), name='template-api-list'),
    url(r'^api/templates/(?P<pk>\d+)/$', TemplateApiDetail.as_view(), name='template-api-detail'),
    url(r'^api/ipaddresses/$', IpAddressApiList.as_view(), name='ipaddress-api-list'),
    url(r'^api/ipaddresses/(?P<pk>\d+)/$', IpAddressApiDetail.as_view(), name='ipaddress-api-detail'),
), allowed=["json", "html"])