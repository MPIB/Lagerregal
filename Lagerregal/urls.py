from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.urls import include
from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

from rest_framework.urlpatterns import format_suffix_patterns

from api.views import *
from devicegroups.views import *
from devices.ajax import AddDeviceField
from devices.ajax import AutocompleteDevice
from devices.ajax import AutocompleteName
from devices.ajax import AutocompleteSmallDevice
from devices.ajax import LoadExtraform
from devices.ajax import LoadMailtemplate
from devices.ajax import PreviewMail
from devices.ajax import PuppetDetails
from devices.ajax import PuppetSoftware
from devices.ajax import UserLendings
from devices.views import *
from devicetags.views import *
from devicetypes.ajax import GetTypeAttributes
from devicetypes.views import *
from history.views import *
from locations.views import *
from mail.views import *
from main.ajax import WidgetAdd
from main.ajax import WidgetMove
from main.ajax import WidgetRemove
from main.ajax import WidgetToggle
from main.views import *
from network.views import *
from users.views import *

from . import settings

urlpatterns = [
    path('', login_required(Home.as_view()), name="home"),

    path('accounts/login/', LoginView.as_view(), name="login"),
    path('accounts/logout/', LogoutView.as_view(), name="logout"),

    path('search/', Search.as_view(), name="search"),

    path('devices/', DeviceList.as_view(), name="device-list"),
    path('devices/page/<int:page>/', DeviceList.as_view(), name="device-list"),
    path('devices/department/<department>/sorting/<sorting>/filter/<filter>/', DeviceList.as_view(), name="device-list"),
    path('devices/page/<int:page>/department/<department>/sorting/<sorting>/filter/<filter>/', DeviceList.as_view(), name="device-list"),
    path('devices/add/', DeviceCreate.as_view(), name="device-add"),
    path('devices/add/template/<int:templateid>/', DeviceCreate.as_view(), name="device-add"),
    path('devices/add/copy/<int:copyid>/', DeviceCreate.as_view(), name="device-add-copy"),
    path('devices/<int:pk>/', DeviceDetail.as_view(), name="device-detail"),
    path('devices/<int:pk>/edit/', DeviceUpdate.as_view(), name="device-edit"),
    path('devices/<int:pk>/delete/', DeviceDelete.as_view(), name="device-delete"),
    path('devices/<int:pk>/archive/', DeviceArchive.as_view(), name="device-archive"),
    path('devices/<int:pk>/trash/', DeviceTrash.as_view(), name="device-trash"),
    path('devices/<int:pk>/storage/', DeviceStorage.as_view(), name="device-storage"),
    path('devices/<int:pk>/mail/', DeviceMail.as_view(), name="device-mail"),
    path('devices/<int:pk>/ipaddress/', DeviceIpAddress.as_view(), name="device-ipaddress"),
    path('devices/<int:pk>/ipaddress/<int:ipaddress>/remove/', DeviceIpAddressRemove.as_view(), name="device-ipaddress-remove"),
    path('devices/<int:pk>/ipaddress/<int:ipaddress>/purpose/', DeviceIpAddressPurpose.as_view(), name="device-ipaddress-purpose"),
    path('devices/<int:pk>/tags/', DeviceTags.as_view(), name="device-tags"),
    path('devices/<int:pk>/tags/<int:tag>/', DeviceTagRemove.as_view(), name="device-tag-remove"),
    path('devices/<int:pk>/lending/', DeviceLendingList.as_view(), name="device-lending-list"),
    path('devices/<int:pk>/lending/page/<int:page>/', DeviceLendingList.as_view(), name="device-lending-list"),
    path('devices/<int:pk>/inventoried/', DeviceInventoried.as_view(), name="device-inventoried"),
    path('devices/<int:pk>/bookmark/', DeviceBookmark.as_view(), name="device-bookmark"),
    path('devices/<int:pk>/notes/create/', NoteCreate.as_view(), name="device-note-create"),
    path('devices/<int:pk>/notes/edit/', NoteUpdate.as_view(), name="device-note-edit"),
    path('devices/<int:device>/notes/<int:pk>/delete/', NoteDelete.as_view(), name="device-note-delete"),
    path('devices/<int:pk>/pictures/create/', PictureCreate.as_view(), name="device-picture-create"),
    path('devices/<int:device>/pictures/<int:pk>/edit/', PictureUpdate.as_view(), name="device-picture-edit"),
    path('devices/<int:device>/pictures/<int:pk>/delete/', PictureDelete.as_view(), name="device-picture-delete"),
    path('devices/lend/', DeviceLend.as_view(), name="device-lend"),
    path('devices/lend/<int:pk>', DeviceLend.as_view(), name="device-lend"),
    path('devices/export/csv/', ExportCsv.as_view(), name='export-csv'),
    path('devices/return/<int:lending>/', DeviceReturn.as_view(), name="device-return"),
    path('devices/public/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/page/<int:page>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/sorting/<sorting>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/page/<int:page>/sorting/<sorting>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/sorting/<sorting>/group/<group>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/page/<int:page>/sorting/<sorting>/group/<group>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/sorting/<sorting>/group/<group>/filter/<filter>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/page/<int:page>/sorting/<sorting>/group/<group>/filter/<filter>/', xframe_options_exempt(PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/<int:pk>/', xframe_options_exempt(PublicDeviceDetailView.as_view()), name="public-device-detail"),
    path('devices/templates/', TemplateList.as_view(), name="template-list"),
    path('devices/templates/page/<int:page>/', TemplateList.as_view(), name="template-list"),
    path('devices/templates/add/', TemplateCreate.as_view(), name="template-add"),
    path('devices/templates/<int:pk>/edit/', TemplateUpdate.as_view(), name="template-edit"),
    path('devices/templates/<int:pk>/delete/', TemplateDelete.as_view(), name="template-delete"),


    path('types/', TypeList.as_view(), name="type-list"),
    path('types/page/<int:page>/', TypeList.as_view(), name="type-list"),
    path('types/sorting/<sorting>/', TypeList.as_view(), name="type-list"),
    path('types/page/<int:page>/sorting/<sorting>/', TypeList.as_view(), name="type-list"),
    path('types/sorting/<sorting>/filter/<filter>/', TypeList.as_view(), name="type-list"),
    path('types/page/<int:page>/sorting/<sorting>/filter/<filter>/', TypeList.as_view(), name="type-list"),
    path('types/add/', TypeCreate.as_view(), name="type-add"),
    path('types/<int:pk>/', TypeDetail.as_view(), name="type-detail"),
    path('types/<int:pk>/edit/', TypeUpdate.as_view(), name="type-edit"),
    path('types/<int:pk>/delete/', TypeDelete.as_view(), name="type-delete"),
    path('types/<int:oldpk>/merge/<int:newpk>/', TypeMerge.as_view(), name="type-merge"),
    path('types/attribute/add/', TypeAttributeCreate.as_view(), name="typeattribute-add"),
    path('types/attribute/<int:pk>/edit/', TypeAttributeUpdate.as_view(), name="typeattribute-edit"),
    path('types/attribute/<int:pk>/delete/', TypeAttributeDelete.as_view(), name="typeattribute-delete"),


    path('rooms/', RoomList.as_view(), name="room-list"),
    path('rooms/page/<int:page>/', RoomList.as_view(), name="room-list"),
    path('rooms/sorting/<sorting>/', RoomList.as_view(), name="room-list"),
    path('rooms/page/<int:page>/sorting/<sorting>/', RoomList.as_view(), name="room-list"),
    path('rooms/sorting/<sorting>/filter/<filter>/', RoomList.as_view(), name="room-list"),
    path('rooms/page/<int:page>/sorting/<sorting>/filter/<filter>/', RoomList.as_view(), name="room-list"),
    path('rooms/add/', RoomCreate.as_view(), name="room-add"),
    path('rooms/<pk>/', RoomDetail.as_view(), name="room-detail"),
    path('rooms/<pk>/edit/', RoomUpdate.as_view(), name="room-edit"),
    path('rooms/<pk>/delete/', RoomDelete.as_view(), name="room-delete"),
    path('rooms/<int:oldpk>/merge/<int:newpk>/', RoomMerge.as_view(), name="room-merge"),

    path('buildings/', BuildingList.as_view(), name="building-list"),
    path('buildings/page/<int:page>/', BuildingList.as_view(), name="building-list"),
    path('buildings/sorting/<sorting>/', BuildingList.as_view(), name="building-list"),
    path('buildings/page/<int:page>/sorting/<sorting>/', BuildingList.as_view(), name="building-list"),
    path('buildings/sorting/<sorting>/filter/<filter>/', BuildingList.as_view(), name="building-list"),
    path('buildings/page/<int:page>/sorting/<sorting>/filter/<filter>/', BuildingList.as_view(), name="building-list"),
    path('buildings/add/', BuildingCreate.as_view(), name="building-add"),
    path('buildings/<pk>/', BuildingDetail.as_view(), name="building-detail"),
    path('buildings/<pk>/edit/', BuildingUpdate.as_view(), name="building-edit"),
    path('buildings/<pk>/delete/', BuildingDelete.as_view(), name="building-delete"),
    path('buildings/<int:oldpk>/merge/<int:newpk>/', BuildingMerge.as_view(), name="building-merge"),

    path('manufacturers/', ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/page/<int:page>/', ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/sorting/<sorting>/', ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/page/<int:page>/sorting/<sorting>/', ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/sorting/<sorting>/filter/<filter>/', ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/page/<int:page>/sorting/<sorting>/filter/<filter>/', ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/add/', ManufacturerCreate.as_view(), name="manufacturer-add"),
    path('manufacturers/<pk>/', ManufacturerDetail.as_view(), name="manufacturer-detail"),
    path('manufacturers/<pk>/edit/', ManufacturerUpdate.as_view(), name="manufacturer-edit"),
    path('manufacturers/<pk>/delete/', ManufacturerDelete.as_view(), name="manufacturer-delete"),
    path('manufacturers/<int:oldpk>/merge/<int:newpk>/', ManufacturerMerge.as_view(), name="manufacturer-merge"),

    path('mails/', MailList.as_view(), name="mail-list"),
    path('mails/page/<int:page>/', MailList.as_view(), name="mail-list"),
    path('mails/add/', MailCreate.as_view(), name="mail-add"),
    path('mails/<pk>/', MailDetail.as_view(), name="mail-detail"),
    path('mails/<pk>/edit/', MailUpdate.as_view(), name="mail-edit"),
    path('mails/<pk>/delete/', MailDelete.as_view(), name="mail-delete"),

    path('devicegroups/', DevicegroupList.as_view(), name="devicegroup-list"),
    path('devicegroups/page/<int:page>/', DevicegroupList.as_view(), name="devicegroup-list"),
    path('devicegroups/department/<department>/sorting/<sorting>/filter/<filter>/', DevicegroupList.as_view(), name="devicegroup-list"),
    path('devicegroups/page/<int:page>/department/<department>/sorting/<sorting>/filter/<filter>/', DevicegroupList.as_view(), name="devicegroup-list"),
    path('devicegroups/add/', DevicegroupCreate.as_view(), name="devicegroup-add"),
    path('devicegroups/<pk>/', DevicegroupDetail.as_view(), name="devicegroup-detail"),
    path('devicegroups/<pk>/edit/', DevicegroupUpdate.as_view(), name="devicegroup-edit"),
    path('devicegroups/<pk>/delete/', DevicegroupDelete.as_view(), name="devicegroup-delete"),

    path('devicetags/', DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/page/<int:page>/', DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/sorting/<sorting>/', DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/page/<int:page>/sorting/<sorting>/', DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/sorting/<sorting>/filter/<filter>/', DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/page/<int:page>/sorting/<sorting>/filter/<filter>/', DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/add/', DevicetagCreate.as_view(), name="devicetag-add"),
    path('devicetags/<pk>/edit/', DevicetagUpdate.as_view(), name="devicetag-edit"),
    path('devicetags/<pk>/delete/', DevicetagDelete.as_view(), name="devicetag-delete"),

    path('sections/', SectionList.as_view(), name="section-list"),
    path('sections/page/<int:page>/', SectionList.as_view(), name="section-list"),
    path('sections/sorting/<sorting>/', SectionList.as_view(), name="section-list"),
    path('sections/page/<int:page>/sorting/<sorting>/', SectionList.as_view(), name="section-list"),
    path('sections/sorting/<sorting>/filter/<filter>/', SectionList.as_view(), name="section-list"),
    path('sections/page/<int:page>/sorting/<sorting>/filter/<filter>/', SectionList.as_view(), name="section-list"),
    path('sections/add/', SectionCreate.as_view(), name="section-add"),
    path('sections/<pk>/', SectionDetail.as_view(), name="section-detail"),
    path('sections/<pk>/edit/', SectionUpdate.as_view(), name="section-edit"),
    path('sections/<pk>/delete/', SectionDelete.as_view(), name="section-delete"),
    path('sections/<int:oldpk>/merge/<int:newpk>/', SectionMerge.as_view(), name="section-merge"),

    path('departments/', DepartmentList.as_view(), name="department-list"),
    path('departments/page/<int:page>/', DepartmentList.as_view(), name="department-list"),
    path('departments/sorting/<sorting>/', DepartmentList.as_view(), name="department-list"),
    path('departments/page/<int:page>/sorting/<sorting>/', DepartmentList.as_view(), name="department-list"),
    path('departments/sorting/<sorting>/filter/<filter>/', DepartmentList.as_view(), name="department-list"),
    path('departments/page/<int:page>/sorting/<sorting>/filter/<filter>/', DepartmentList.as_view(), name="department-list"),
    path('departments/add/', DepartmentCreate.as_view(), name="department-add"),
    path('departments/<pk>/', DepartmentDetail.as_view(), name="department-detail"),
    path('departments/<pk>/edit/', DepartmentUpdate.as_view(), name="department-edit"),
    path('departments/<pk>/adduser/', DepartmentAddUser.as_view(), name="department-add-user"),
    path('departments/<pk>/removeuser/', DepartmentDeleteUser.as_view(), name="department-remove-user"),
    path('departments/<pk>/delete/', DepartmentDelete.as_view(), name="department-delete"),

    path('ipaddresses/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/department/<department>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/department/<department>/filter/<filter>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/department/<department>/filter/<filter>/search/<search>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/page/<int:page>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/page/<int:page>/department/<department>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/page/<int:page>/department/<department>/filter/<filter>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/page/<int:page>/department/<department>/filter/<filter>/search/<search>/', IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/add/', IpAddressCreate.as_view(), name="ipaddress-add"),
    path('ipaddresses/<pk>/', IpAddressDetail.as_view(), name="ipaddress-detail"),
    path('ipaddresses/<pk>/edit/', IpAddressUpdate.as_view(), name="ipaddress-edit"),
    path('ipaddresses/<pk>/delete/', IpAddressDelete.as_view(), name="ipaddress-delete"),

    path('users/', UserList.as_view(), name="user-list"),
    path('users/department/<department>/filter/<filter>/', UserList.as_view(), name="user-list"),
    path('users/page/<int:page>/department/<department>/filter/<filter>/', UserList.as_view(), name="user-list"),
    path('users/<int:pk>/', ProfileView.as_view(), name="userprofile"),
    path('users/<int:pk>/ipaddress/', UserIpAddress.as_view(), name="user-ipaddress"),
    path('users/<int:pk>/ipaddress/<int:ipaddress>/', UserIpAddressRemove.as_view(), name="user-ipaddress-remove"),
    path('profile/', login_required(UserprofileView.as_view()), name="userprofile"),
    path('settings/', login_required(UsersettingsView.as_view()), name="usersettings"),

    path('history/global/', Globalhistory.as_view(), name="globalhistory"),
    path('history/global/page/<int:page>/', Globalhistory.as_view(), name="globalhistory"),
    path('history/<int:content_type_id>/<int:object_id>/', HistoryList.as_view(), name="history-list"),
    path('history/<int:content_type_id>/<int:object_id>/page/<int:page>/', HistoryList.as_view(), name="history-list"),
    path('history/version/<int:pk>/', HistoryDetail.as_view(), name="history-detail"),

    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    path('', include('favicon.urls')),

    path('ajax/add_widget/', login_required(WidgetAdd.as_view()), name="widget_add"),
    path('ajax/remove_widget/', login_required(WidgetRemove.as_view()), name="widget_remove"),
    path('ajax/toggle_widget/', login_required(WidgetToggle.as_view()), name="widget_toggle"),
    path('ajax/move_widget/', login_required(WidgetMove.as_view()), name="widget_move"),
    path('ajax/autocomplete_name/', login_required(AutocompleteName.as_view()), name="autocomplete-name"),
    path('ajax/autocomplete_device/', login_required(AutocompleteDevice.as_view()), name="autocomplete-device"),
    path('ajax/autocomplete_smalldevice/', login_required(AutocompleteSmallDevice.as_view()), name="autocomplete-smalldevice"),
    path('ajax/load_extraform/', login_required(LoadExtraform.as_view()), name="load-extraform"),
    path('ajax/load_mailtemplate/', login_required(LoadMailtemplate.as_view()), name="load-mailtemplate"),
    path('ajax/preview_mail/', login_required(PreviewMail.as_view()), name="preview-mail"),
    path('ajax/add_device_field/', login_required(AddDeviceField.as_view()), name="add-device-field"),
    path('ajax/get_attributes/', login_required(GetTypeAttributes.as_view()), name="get-attributes"),
    path('ajax/user_lendings/', login_required(UserLendings.as_view()), name="get-user-lendings"),
    path('ajax/puppetdetails/', login_required(PuppetDetails.as_view()), name="puppet-details"),
    path('ajax/puppetsoftware/', login_required(PuppetSoftware.as_view()), name="puppet-software"),
]

urlpatterns += format_suffix_patterns([
    path('api/', api_root),
    path('api/devices/', DeviceApiList.as_view(), name='device-api-list'),
    path('api/devices/create/', DeviceApiCreate.as_view(), name='device-api-create'),
    path('api/devices/<int:pk>/', DeviceApiDetail.as_view(), name='device-api-detail'),
    path('api/devices/<int:pk>/bookmark/', DeviceApiBookmark.as_view(), name='device-api-bookmark'),
    path('api/devices/<int:pk>/changeroom/', DeviceApiRoomChange.as_view(), name='device-api-room'),
    path('api/devices/<int:pk>/pictures/', DeviceApiListPictures.as_view(), name='device-api-pictures'),
    path('api/devices/<device>/pictures/<int:pk>/', DeviceApiPicture.as_view(), name='device-api-picture'),
    path('api/devices/<device>/pictures/<int:pk>/rotate/<orientation>/', DeviceApiPictureRotate.as_view(), name='device-api-picture-rotate'),
    path('api/devices/lend/', DeviceApiLend.as_view(), name='device-api-lend'),
    path('api/devices/return/', DeviceApiReturn.as_view(), name='device-api-return'),
    path('api/smalldevices/', SmallDeviceApiList.as_view(), name='smalldevice-api-lend'),
    path('api/smalldevices/<subpart>/', SmallDeviceApiList.as_view(), name='smalldevice-api-lend'),


    path('api/manufacturers/', ManufacturerApiList.as_view(), name='manufacturer-api-list'),
    path('api/manufacturers/create/', ManufacturerApiCreate.as_view(), name='manufacturer-api-create'),
    path('api/manufacturers/<int:pk>/', ManufacturerApiDetail.as_view(), name='manufacturer-api-detail'),

    path('api/rooms/', RoomApiList.as_view(), name='room-api-list'),
    path('api/rooms/create/', RoomApiCreate.as_view(), name='room-api-create'),
    path('api/rooms/<int:pk>/', RoomApiDetail.as_view(), name='room-api-detail'),

    path('api/types/', TypeApiList.as_view(), name='type-api-list'),
    path('api/types/create/', TypeApiCreate.as_view(), name='type-api-create'),
    path('api/types/<int:pk>/', TypeApiDetail.as_view(), name='type-api-detail'),

    path('api/buildings/', BuildingApiList.as_view(), name='building-api-list'),
    path('api/buildings/create/', BuildingApiCreate.as_view(), name='building-api-create'),
    path('api/buildings/<int:pk>/', BuildingApiDetail.as_view(), name='building-api-detail'),

    path('api/templates/', TemplateApiList.as_view(), name='template-api-list'),
    path('api/templates/create/', TemplateApiCreate.as_view(), name='template-api-create'),
    path('api/templates/<int:pk>/', TemplateApiDetail.as_view(), name='template-api-detail'),

    path('api/ipaddresses/', IpAddressApiList.as_view(), name='ipaddress-api-list'),
    path('api/ipaddresses/create/', IpAddressApiCreate.as_view(), name='ipaddress-api-create'),
    path('api/ipaddresses/<int:pk>/', IpAddressApiDetail.as_view(), name='ipaddress-api-detail'),

    path('api/users/', UserApiList.as_view(), name='user-api-list'),
    path('api/users/<int:pk>/', UserApiDetail.as_view(), name='user-api-detail'),
    path('api/users/profile/', UserApiProfile.as_view(), name='user-api-profile'),
    path('api/useravatar/<username>/', UserApiAvatar.as_view(), name='user-api-avatar'),

    path('api/groups/', GroupApiList.as_view(), name='group-api-list'),
    path('api/groups/<int:pk>/', GroupApiDetail.as_view(), name='group-api-detail'),

    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
], allowed=["json", "html"])

if settings.DEBUG:
    import debug_toolbar
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path('media/<path:path>', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
