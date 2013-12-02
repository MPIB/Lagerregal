from devices.models import Room, Building, Manufacturer, Device, Template, Lending
from devicetypes.models import Type, TypeAttribute
from rest_framework import serializers

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

class TypeNameSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='type-api-detail')
    class Meta:
        model = Type

class TypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='type-api-detail')
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
    creator = serializers.SlugRelatedField(slug_field="username")
    currentlending = LendingSerializer()

    class Meta:
        model = Device

class DeviceListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='device-api-detail')

    class Meta:
        model = Device
        fields = ("url", "name")