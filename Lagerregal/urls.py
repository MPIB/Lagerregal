from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import include
from django.urls import path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve

from rest_framework.urlpatterns import format_suffix_patterns

from api import views as api_views
from devicegroups import views as devicegroups_views
from devices import ajax as devices_ajax
from devices import views as devices_views
from devicetags import views as devicetags_views
from devicetypes import ajax as devicetypes_ajax
from devicetypes import views as devicetypes_views
from history import views as history_views
from locations import views as locations_views
from mail import views as mail_views
from main import ajax as main_ajax
from main import views as main_views
from network import views as network_views
from users import views as users_views

from . import settings

urlpatterns = [
    path('', login_required(main_views.Home.as_view()), name="home"),

    path('accounts/login/', auth_views.LoginView.as_view(), name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),

    path('search/', devices_views.Search.as_view(), name="search"),

    path('devices/', devices_views.DeviceList.as_view(), name="device-list"),
    path('devices/add/', devices_views.DeviceCreate.as_view(), name="device-add"),
    path('devices/add/template/<int:templateid>/', devices_views.DeviceCreate.as_view(), name="device-add"),
    path('devices/add/copy/<int:copyid>/', devices_views.DeviceCreate.as_view(), name="device-add-copy"),
    path('devices/<int:pk>/', devices_views.DeviceDetail.as_view(), name="device-detail"),
    path('devices/<int:pk>/edit/', devices_views.DeviceUpdate.as_view(), name="device-edit"),
    path('devices/<int:pk>/delete/', devices_views.DeviceDelete.as_view(), name="device-delete"),
    path('devices/<int:pk>/archive/', devices_views.DeviceArchive.as_view(), name="device-archive"),
    path('devices/<int:pk>/trash/', devices_views.DeviceTrash.as_view(), name="device-trash"),
    path('devices/<int:pk>/storage/', devices_views.DeviceStorage.as_view(), name="device-storage"),
    path('devices/<int:pk>/mail/', devices_views.DeviceMail.as_view(), name="device-mail"),
    path('devices/<int:pk>/ipaddress/', devices_views.DeviceIpAddress.as_view(), name="device-ipaddress"),
    path('devices/<int:pk>/ipaddress/<int:ipaddress>/remove/', devices_views.DeviceIpAddressRemove.as_view(), name="device-ipaddress-remove"),
    path('devices/<int:pk>/ipaddress/<int:ipaddress>/purpose/', devices_views.DeviceIpAddressPurpose.as_view(), name="device-ipaddress-purpose"),
    path('devices/<int:pk>/tags/', devicetags_views.DeviceTags.as_view(), name="device-tags"),
    path('devices/<int:pk>/tags/<int:tag>/', devicetags_views.DeviceTagRemove.as_view(), name="device-tag-remove"),
    path('devices/<int:pk>/lending/', devices_views.DeviceLendingList.as_view(), name="device-lending-list"),
    path('devices/<int:pk>/inventoried/', devices_views.DeviceInventoried.as_view(), name="device-inventoried"),
    path('devices/<int:pk>/bookmark/', devices_views.DeviceBookmark.as_view(), name="device-bookmark"),
    path('devices/<int:pk>/notes/create/', devices_views.NoteCreate.as_view(), name="device-note-create"),
    path('devices/<int:pk>/notes/edit/', devices_views.NoteUpdate.as_view(), name="device-note-edit"),
    path('devices/<int:device>/notes/<int:pk>/delete/', devices_views.NoteDelete.as_view(), name="device-note-delete"),
    path('devices/<int:pk>/pictures/create/', devices_views.PictureCreate.as_view(), name="device-picture-create"),
    path('devices/<int:device>/pictures/<int:pk>/edit/', devices_views.PictureUpdate.as_view(), name="device-picture-edit"),
    path('devices/<int:device>/pictures/<int:pk>/delete/', devices_views.PictureDelete.as_view(), name="device-picture-delete"),
    path('devices/lend/', devices_views.DeviceLend.as_view(), name="device-lend"),
    path('devices/lend/<int:pk>', devices_views.DeviceLend.as_view(), name="device-lend"),
    path('devices/export/csv/', devices_views.ExportCsv.as_view(), name='export-csv'),
    path('devices/return/<int:lending>/', devices_views.DeviceReturn.as_view(), name="device-return"),
    path('devices/public/', xframe_options_exempt(devices_views.PublicDeviceListView.as_view()), name="public-device-list"),
    path('devices/public/<int:pk>/', xframe_options_exempt(devices_views.PublicDeviceDetailView.as_view()), name="public-device-detail"),
    path('devices/templates/', devices_views.TemplateList.as_view(), name="template-list"),
    path('devices/templates/add/', devices_views.TemplateCreate.as_view(), name="template-add"),
    path('devices/templates/<int:pk>/edit/', devices_views.TemplateUpdate.as_view(), name="template-edit"),
    path('devices/templates/<int:pk>/delete/', devices_views.TemplateDelete.as_view(), name="template-delete"),


    path('types/', devicetypes_views.TypeList.as_view(), name="type-list"),
    path('types/add/', devicetypes_views.TypeCreate.as_view(), name="type-add"),
    path('types/<int:pk>/', devicetypes_views.TypeDetail.as_view(), name="type-detail"),
    path('types/<int:pk>/edit/', devicetypes_views.TypeUpdate.as_view(), name="type-edit"),
    path('types/<int:pk>/delete/', devicetypes_views.TypeDelete.as_view(), name="type-delete"),
    path('types/<int:oldpk>/merge/<int:newpk>/', devicetypes_views.TypeMerge.as_view(), name="type-merge"),
    path('types/attribute/add/', devicetypes_views.TypeAttributeCreate.as_view(), name="typeattribute-add"),
    path('types/attribute/<int:pk>/edit/', devicetypes_views.TypeAttributeUpdate.as_view(), name="typeattribute-edit"),
    path('types/attribute/<int:pk>/delete/', devicetypes_views.TypeAttributeDelete.as_view(), name="typeattribute-delete"),


    path('rooms/', devices_views.RoomList.as_view(), name="room-list"),
    path('rooms/add/', devices_views.RoomCreate.as_view(), name="room-add"),
    path('rooms/<int:pk>/', devices_views.RoomDetail.as_view(), name="room-detail"),
    path('rooms/<int:pk>/edit/', devices_views.RoomUpdate.as_view(), name="room-edit"),
    path('rooms/<int:pk>/delete/', devices_views.RoomDelete.as_view(), name="room-delete"),
    path('rooms/<int:oldpk>/merge/<int:newpk>/', devices_views.RoomMerge.as_view(), name="room-merge"),

    path('buildings/', devices_views.BuildingList.as_view(), name="building-list"),
    path('buildings/add/', devices_views.BuildingCreate.as_view(), name="building-add"),
    path('buildings/<int:pk>/', devices_views.BuildingDetail.as_view(), name="building-detail"),
    path('buildings/<int:pk>/edit/', devices_views.BuildingUpdate.as_view(), name="building-edit"),
    path('buildings/<int:pk>/delete/', devices_views.BuildingDelete.as_view(), name="building-delete"),
    path('buildings/<int:oldpk>/merge/<int:newpk>/', devices_views.BuildingMerge.as_view(), name="building-merge"),

    path('manufacturers/', devices_views.ManufacturerList.as_view(), name="manufacturer-list"),
    path('manufacturers/add/', devices_views.ManufacturerCreate.as_view(), name="manufacturer-add"),
    path('manufacturers/<int:pk>/', devices_views.ManufacturerDetail.as_view(), name="manufacturer-detail"),
    path('manufacturers/<int:pk>/edit/', devices_views.ManufacturerUpdate.as_view(), name="manufacturer-edit"),
    path('manufacturers/<int:pk>/delete/', devices_views.ManufacturerDelete.as_view(), name="manufacturer-delete"),
    path('manufacturers/<int:oldpk>/merge/<int:newpk>/', devices_views.ManufacturerMerge.as_view(), name="manufacturer-merge"),

    path('mails/', mail_views.MailList.as_view(), name="mail-list"),
    path('mails/add/', mail_views.MailCreate.as_view(), name="mail-add"),
    path('mails/<int:pk>/', mail_views.MailDetail.as_view(), name="mail-detail"),
    path('mails/<int:pk>/edit/', mail_views.MailUpdate.as_view(), name="mail-edit"),
    path('mails/<int:pk>/delete/', mail_views.MailDelete.as_view(), name="mail-delete"),

    path('devicegroups/', devicegroups_views.DevicegroupList.as_view(), name="devicegroup-list"),
    path('devicegroups/add/', devicegroups_views.DevicegroupCreate.as_view(), name="devicegroup-add"),
    path('devicegroups/<int:pk>/', devicegroups_views.DevicegroupDetail.as_view(), name="devicegroup-detail"),
    path('devicegroups/<int:pk>/edit/', devicegroups_views.DevicegroupUpdate.as_view(), name="devicegroup-edit"),
    path('devicegroups/<int:pk>/delete/', devicegroups_views.DevicegroupDelete.as_view(), name="devicegroup-delete"),

    path('devicetags/', devicetags_views.DevicetagList.as_view(), name="devicetag-list"),
    path('devicetags/add/', devicetags_views.DevicetagCreate.as_view(), name="devicetag-add"),
    path('devicetags/<int:pk>/edit/', devicetags_views.DevicetagUpdate.as_view(), name="devicetag-edit"),
    path('devicetags/<int:pk>/delete/', devicetags_views.DevicetagDelete.as_view(), name="devicetag-delete"),

    path('sections/', locations_views.SectionList.as_view(), name="section-list"),
    path('sections/add/', locations_views.SectionCreate.as_view(), name="section-add"),
    path('sections/<int:pk>/', locations_views.SectionDetail.as_view(), name="section-detail"),
    path('sections/<int:pk>/edit/', locations_views.SectionUpdate.as_view(), name="section-edit"),
    path('sections/<int:pk>/delete/', locations_views.SectionDelete.as_view(), name="section-delete"),
    path('sections/<int:oldpk>/merge/<int:newpk>/', locations_views.SectionMerge.as_view(), name="section-merge"),

    path('departments/', users_views.DepartmentList.as_view(), name="department-list"),
    path('departments/add/', users_views.DepartmentCreate.as_view(), name="department-add"),
    path('departments/<int:pk>/', users_views.DepartmentDetail.as_view(), name="department-detail"),
    path('departments/<int:pk>/edit/', users_views.DepartmentUpdate.as_view(), name="department-edit"),
    path('departments/<int:pk>/adduser/', users_views.DepartmentAddUser.as_view(), name="department-add-user"),
    path('departments/<int:pk>/removeuser/', users_views.DepartmentDeleteUser.as_view(), name="department-remove-user"),
    path('departments/<int:pk>/delete/', users_views.DepartmentDelete.as_view(), name="department-delete"),

    path('ipaddresses/', network_views.IpAddressList.as_view(), name="ipaddress-list"),
    path('ipaddresses/add/', network_views.IpAddressCreate.as_view(), name="ipaddress-add"),
    path('ipaddresses/<int:pk>/', network_views.IpAddressDetail.as_view(), name="ipaddress-detail"),
    path('ipaddresses/<int:pk>/edit/', network_views.IpAddressUpdate.as_view(), name="ipaddress-edit"),
    path('ipaddresses/<int:pk>/delete/', network_views.IpAddressDelete.as_view(), name="ipaddress-delete"),

    path('users/', users_views.UserList.as_view(), name="user-list"),
    path('users/<int:pk>/', users_views.ProfileView.as_view(), name="userprofile"),
    path('users/<int:pk>/ipaddress/', network_views.UserIpAddress.as_view(), name="user-ipaddress"),
    path('users/<int:pk>/ipaddress/<int:ipaddress>/', network_views.UserIpAddressRemove.as_view(), name="user-ipaddress-remove"),
    path('profile/', login_required(users_views.UserprofileView.as_view()), name="userprofile"),
    path('settings/', login_required(users_views.UsersettingsView.as_view()), name="usersettings"),

    path('history/global/', history_views.Globalhistory.as_view(), name="globalhistory"),
    path('history/<int:content_type_id>/<int:object_id>/', history_views.HistoryList.as_view(), name="history-list"),
    path('history/version/<int:pk>/', history_views.HistoryDetail.as_view(), name="history-detail"),

    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),

    path('', include('favicon.urls')),

    path('devices_ajax/add_widget/', login_required(main_ajax.WidgetAdd.as_view()), name="widget_add"),
    path('devices_ajax/remove_widget/', login_required(main_ajax.WidgetRemove.as_view()), name="widget_remove"),
    path('devices_ajax/toggle_widget/', login_required(main_ajax.WidgetToggle.as_view()), name="widget_toggle"),
    path('devices_ajax/move_widget/', login_required(main_ajax.WidgetMove.as_view()), name="widget_move"),
    path('devices_ajax/autocomplete_name/', login_required(devices_ajax.AutocompleteName.as_view()), name="autocomplete-name"),
    path('devices_ajax/autocomplete_device/', login_required(devices_ajax.AutocompleteDevice.as_view()), name="autocomplete-device"),
    path('devices_ajax/autocomplete_smalldevice/', login_required(devices_ajax.AutocompleteSmallDevice.as_view()), name="autocomplete-smalldevice"),
    path('devices_ajax/load_extraform/', login_required(devices_ajax.LoadExtraform.as_view()), name="load-extraform"),
    path('devices_ajax/load_mailtemplate/', login_required(devices_ajax.LoadMailtemplate.as_view()), name="load-mailtemplate"),
    path('devices_ajax/preview_mail/', login_required(devices_ajax.PreviewMail.as_view()), name="preview-mail"),
    path('devices_ajax/add_device_field/', login_required(devices_ajax.AddDeviceField.as_view()), name="add-device-field"),
    path('devices_ajax/get_attributes/', login_required(devicetypes_ajax.GetTypeAttributes.as_view()), name="get-attributes"),
    path('devices_ajax/user_lendings/', login_required(devices_ajax.UserLendings.as_view()), name="get-user-lendings"),
    path('devices_ajax/puppetdetails/<int:device>/', login_required(devices_ajax.PuppetDetails.as_view()), name="puppet-details"),
    path('devices_ajax/puppetsoftware/<int:device>/', login_required(devices_ajax.PuppetSoftware.as_view()), name="puppet-software"),
]

urlpatterns += format_suffix_patterns([
    path('api/', api_views.api_root),
    path('api/devices/', api_views.DeviceApiList.as_view(), name='device-api-list'),
    path('api/devices/create/', api_views.DeviceApiCreate.as_view(), name='device-api-create'),
    path('api/devices/<int:pk>/', api_views.DeviceApiDetail.as_view(), name='device-api-detail'),
    path('api/devices/<int:pk>/bookmark/', api_views.DeviceApiBookmark.as_view(), name='device-api-bookmark'),
    path('api/devices/<int:pk>/changeroom/', api_views.DeviceApiRoomChange.as_view(), name='device-api-room'),
    path('api/devices/<int:pk>/pictures/', api_views.DeviceApiListPictures.as_view(), name='device-api-pictures'),
    path('api/devices/<int:device>/pictures/<int:pk>/', api_views.DeviceApiPicture.as_view(), name='device-api-picture'),
    path('api/devices/<int:device>/pictures/<int:pk>/rotate/<orientation>/', api_views.DeviceApiPictureRotate.as_view(), name='device-api-picture-rotate'),
    path('api/devices/lend/', api_views.DeviceApiLend.as_view(), name='device-api-lend'),
    path('api/devices/return/', api_views.DeviceApiReturn.as_view(), name='device-api-return'),
    path('api/smalldevices/', api_views.SmallDeviceApiList.as_view(), name='smalldevice-api-lend'),
    path('api/smalldevices/<subpart>/', api_views.SmallDeviceApiList.as_view(), name='smalldevice-api-lend'),


    path('api/manufacturers/', api_views.ManufacturerApiList.as_view(), name='manufacturer-api-list'),
    path('api/manufacturers/create/', api_views.ManufacturerApiCreate.as_view(), name='manufacturer-api-create'),
    path('api/manufacturers/<int:pk>/', api_views.ManufacturerApiDetail.as_view(), name='manufacturer-api-detail'),

    path('api/rooms/', api_views.RoomApiList.as_view(), name='room-api-list'),
    path('api/rooms/create/', api_views.RoomApiCreate.as_view(), name='room-api-create'),
    path('api/rooms/<int:pk>/', api_views.RoomApiDetail.as_view(), name='room-api-detail'),

    path('api/types/', api_views.TypeApiList.as_view(), name='type-api-list'),
    path('api/types/create/', api_views.TypeApiCreate.as_view(), name='type-api-create'),
    path('api/types/<int:pk>/', api_views.TypeApiDetail.as_view(), name='type-api-detail'),

    path('api/buildings/', api_views.BuildingApiList.as_view(), name='building-api-list'),
    path('api/buildings/create/', api_views.BuildingApiCreate.as_view(), name='building-api-create'),
    path('api/buildings/<int:pk>/', api_views.BuildingApiDetail.as_view(), name='building-api-detail'),

    path('api/templates/', api_views.TemplateApiList.as_view(), name='template-api-list'),
    path('api/templates/create/', api_views.TemplateApiCreate.as_view(), name='template-api-create'),
    path('api/templates/<int:pk>/', api_views.TemplateApiDetail.as_view(), name='template-api-detail'),

    path('api/ipaddresses/', api_views.IpAddressApiList.as_view(), name='ipaddress-api-list'),
    path('api/ipaddresses/create/', api_views.IpAddressApiCreate.as_view(), name='ipaddress-api-create'),
    path('api/ipaddresses/<int:pk>/', api_views.IpAddressApiDetail.as_view(), name='ipaddress-api-detail'),

    path('api/users/', api_views.UserApiList.as_view(), name='user-api-list'),
    path('api/users/<int:pk>/', api_views.UserApiDetail.as_view(), name='user-api-detail'),
    path('api/users/profile/', api_views.UserApiProfile.as_view(), name='user-api-profile'),
    path('api/useravatar/<username>/', api_views.UserApiAvatar.as_view(), name='user-api-avatar'),

    path('api/groups/', api_views.GroupApiList.as_view(), name='group-api-list'),
    path('api/groups/<int:pk>/', api_views.GroupApiDetail.as_view(), name='group-api-detail'),

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
