from network.models import IpAddress
from rest_framework import serializers

class IpAddressSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipaddress-api-detail')

    device = serializers.SlugRelatedField(slug_field="name")
    class Meta:
        model = IpAddress

