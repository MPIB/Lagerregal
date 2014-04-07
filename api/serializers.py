from devices.models import Room, Building, Manufacturer, Device, Template, Lending
from devicetypes.models import Type, TypeAttribute
from rest_framework import serializers
from users.models import Lageruser
from django.contrib.auth.models import Group, Permission
from network.models import IpAddress

class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='building-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    class Meta:
        model = Building


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='room-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    building = BuildingSerializer()

    class Meta:
        model = Room

class ManufacturerSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='manufacturer-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Manufacturer

class TypeAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeAttribute
        exclude = ("devicetype", )

class TypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='type-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    typeattribute_set = TypeAttributeSerializer()
    class Meta:
        model = Type

class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='template-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Template

class LendingSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field="username")

    class Meta:
        model = Lending

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    manufacturer = serializers.SlugRelatedField(slug_field="name")
    room = serializers.SlugRelatedField(slug_field="name")
    devicetype = serializers.SlugRelatedField(slug_field="name")
    ip_addresses = serializers.SlugRelatedField(many=True, source='ipaddress_set', slug_field="address")
    creator = serializers.HyperlinkedIdentityField(view_name='user-api-detail')
    currentlending = LendingSerializer()
    bookmarked = serializers.BooleanField()

    class Meta:
        model = Device
        exclude = ("bookmarkers", )

class DeviceListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Device
        fields = ("url", "name")

class LendingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lending
        exclude = ("lenddate", "duedate_email", "returndate")

    def validate(self, attrs):
        if attrs["device"] and attrs["smalldevice"]:
            raise serializers.ValidationError("can not set both device and smalldevice")
        elif not attrs["device"] and not attrs["smalldevice"]:
            raise serializers.ValidationError("you have to either set device or smalldevice")
        elif attrs["device"]:
            if attrs["device"].currentlending:
                raise serializers.ValidationError("this device is already lend.")
        return attrs


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
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
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Lageruser
        fields = ("url", "username", "first_name", "last_name", "email")


class IpAddressSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipaddress-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    device = serializers.SlugRelatedField(slug_field="name")
    class Meta:
        model = IpAddress
