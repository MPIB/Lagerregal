from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from rest_framework import serializers

from devices.models import Building
from devices.models import Device
from devices.models import Lending
from devices.models import Manufacturer
from devices.models import Picture
from devices.models import Room
from devices.models import Template
from devicetypes.models import Type
from devicetypes.models import TypeAttribute
from network.models import IpAddress
from users.models import Department
from users.models import Lageruser


class BuildingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='building-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Building
        exclude = ()


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='room-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    building = BuildingSerializer()

    class Meta:
        model = Room
        exclude = ()


class ManufacturerSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='manufacturer-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Manufacturer
        exclude = ()


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
        exclude = ()


class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='template-api-detail')
    id = serializers.CharField(source="pk", read_only=True)

    class Meta:
        model = Template
        exclude = ()


class LendingDisplaySerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    owner_url = serializers.HyperlinkedIdentityField(source="owner", view_name='user-api-detail')

    class Meta:
        model = Lending
        exclude = ()


class PictureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Picture
        fields = ("id", "image", "caption")


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    manufacturer = serializers.SlugRelatedField(slug_field="name", queryset=Manufacturer.objects.all())
    room = serializers.SlugRelatedField(slug_field="name", queryset=Room.objects.select_related("building").all())
    devicetype = serializers.SlugRelatedField(slug_field="name", queryset=Type.objects.all())
    ip_addresses = serializers.SlugRelatedField(many=True, source='ipaddress_set', slug_field="address", queryset=IpAddress.objects.all())
    creator = serializers.StringRelatedField(read_only=True)
    creator_url = serializers.HyperlinkedIdentityField(view_name='user-api-detail')
    currentlending = LendingDisplaySerializer(required=False, read_only=True)
    bookmarked = serializers.BooleanField()
    department = serializers.SlugRelatedField(slug_field="name", queryset=Department.objects.all())
    pictures = PictureSerializer(many=True, read_only=True)
    contact = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Device
        exclude = ("bookmarkers", )


class DeviceListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    department = serializers.SlugRelatedField(slug_field="name", queryset=Department.objects.all())

    class Meta:
        model = Device
        fields = ("url", "id", "name", "department")


class DeviceRoomSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.select_related("building").all())

    class Meta:
        model = Device
        fields = ("url", "id", "room")


class LendingSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.select_related("building").all(), required=False)

    class Meta:
        model = Lending
        exclude = ("lenddate", "duedate_email", "returndate")

    def validate(self, attrs):
        if "smalldevice" in attrs and "device" in attrs:
            if attrs["device"] and attrs["smalldevice"]:
                raise serializers.ValidationError("can not set both device and smalldevice")
            elif not attrs["device"] and not attrs["smalldevice"]:
                raise serializers.ValidationError("you have to either set device or smalldevice")
        elif "smalldevice" not in attrs and "device" not in attrs:
            raise serializers.ValidationError("you have to either set device or smalldevice")
        if "device" in attrs:
            if attrs["device"] != "" and attrs["device"] is not None:
                if attrs["device"].currentlending:
                    raise serializers.ValidationError("this device is already lend.")
        return attrs

    def restore_object(self, attrs, instance=None):
        if self.context["request"].POST:
            del attrs["room"]
            del self.fields["room"]
        obj = super().restore_object(attrs, instance=instance)
        return obj

    def to_native(self, obj):
        if self.context["request"].POST:
            if "room" in self.fields:
                del self.fields["room"]
        return super().to_native(obj)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    groups = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Group.objects.all())
    user_permissions = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Permission.objects.all())
    main_department = serializers.SlugRelatedField(slug_field="name", read_only=True)
    departments = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Department.objects.all())

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
        fields = ("url", "id", "username", "first_name", "last_name", "email")


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='group-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    users = UserListSerializer(many=True, source="user_set")
    permissions = serializers.SlugRelatedField(slug_field="name", many=True, queryset=Permission.objects.all())

    class Meta:
        model = Group
        exclude = ()


class IpAddressSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipaddress-api-detail')
    id = serializers.CharField(source="pk", read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    device = serializers.SlugRelatedField(slug_field="name", queryset=Device.objects.all())

    class Meta:
        model = IpAddress
        exclude = ()
