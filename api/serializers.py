from devices.models import Room, Building, Manufacturer, Device, Template, Lending
from devicetypes.models import Type, TypeAttribute
from rest_framework import serializers
from users.models import Lageruser
from django.contrib.auth.models import Group, Permission
from network.models import IpAddress

class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='building-api-detail')
    class Meta:
        model = Building


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='room-api-detail')
    building = BuildingSerializer()

    class Meta:
        model = Room

class ManufacturerSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='manufacturer-api-detail')

    class Meta:
        model = Manufacturer

class TypeAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeAttribute
        exclude = ("devicetype", )

class TypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='type-api-detail')
    typeattribute_set = TypeAttributeSerializer()
    class Meta:
        model = Type

class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='template-api-detail')

    class Meta:
        model = Template

class LendingSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="username")

    class Meta:
        model = Lending

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')
    manufacturer = serializers.SlugRelatedField(slug_field="name")
    room = serializers.SlugRelatedField(slug_field="name")
    devicetype = serializers.SlugRelatedField(slug_field="name")
    ip_addresses = serializers.SlugRelatedField(many=True, source='ipaddress_set', slug_field="address")
    creator = serializers.HyperlinkedIdentityField(view_name='user-api-detail')
    currentlending = LendingSerializer()

    class Meta:
        model = Device

class DeviceListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')

    class Meta:
        model = Device
        fields = ("url", "name")

class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-api-detail')
    groups = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Group.objects.all())
    user_permissions = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Permission.objects.all())

    class Meta:
        model = Lageruser
        exclude = ("password", )

class UserAvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lageruser
        fields = ("username", "avatar")

class UserListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-api-detail')

    class Meta:
        model = Lageruser
        fields = ("url", "username", "first_name", "last_name", "email")


class IpAddressSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipaddress-api-detail')

    device = serializers.SlugRelatedField(slug_field="name")
    class Meta:
        model = IpAddress
