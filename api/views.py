from api.serializers import *
from devices.models import *
from devicetypes.models import *
from network.models import *
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
import rest_framework.reverse
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'devices': rest_framework.reverse.reverse('device-api-list', request=request),
        'rooms': rest_framework.reverse.reverse('room-api-list', request=request),
        'buildings': rest_framework.reverse.reverse('building-api-list', request=request),
        'manufacturers': rest_framework.reverse.reverse('manufacturer-api-list', request=request),
        'types': rest_framework.reverse.reverse('type-api-list', request=request),
        'templates': rest_framework.reverse.reverse('template-api-list', request=request),
        'ipaddresses': rest_framework.reverse.reverse('ipaddress-api-list', request=request),
        'users': rest_framework.reverse.reverse('user-api-list', request=request),
    })


class SearchQuerysetMixin():
    def get_queryset(self):
        queryset = self.model.objects.all()
        valid_fields = self.model._meta.get_all_field_names()
        filters = {}
        for param in self.request.QUERY_PARAMS.lists():
            if param[0] in valid_fields:
                filters[param[0]]=param[1][0]
        queryset = queryset.filter(**filters)
        return queryset


class DeviceApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Device
    serializer_class = DeviceListSerializer

class DeviceApiCreate(generics.CreateAPIView):
    model = Device
    serializer_class = DeviceSerializer

class DeviceApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Device
    serializer_class = DeviceSerializer


class TypeApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Type
    serializer_class = TypeSerializer

class TypeApiCreate(generics.CreateAPIView):
    model = Type
    serializer_class = TypeSerializer

class TypeApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Type
    serializer_class = TypeSerializer       


class RoomApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Room
    serializer_class = RoomSerializer

class RoomApiCreate(generics.CreateAPIView):
    model = Room
    serializer_class = RoomSerializer

class RoomApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Room
    serializer_class = RoomSerializer


class BuildingApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Building
    serializer_class = BuildingSerializer

class BuildingApiCreate(generics.CreateAPIView):
    model = Building
    serializer_class = BuildingSerializer

class BuildingApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Building
    serializer_class = BuildingSerializer


class ManufacturerApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Manufacturer
    serializer_class = ManufacturerSerializer

class ManufacturerApiCreate(generics.CreateAPIView):
    model = Manufacturer
    serializer_class = ManufacturerSerializer

class ManufacturerApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Manufacturer
    serializer_class = ManufacturerSerializer


class TemplateApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Template
    serializer_class = TemplateSerializer

class TemplateApiCreate(generics.CreateAPIView):
    model = Template
    serializer_class = TemplateSerializer

class TemplateApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Template
    serializer_class = TemplateSerializer


class UserApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Lageruser
    serializer_class = UserListSerializer

class UserApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Lageruser
    serializer_class = UserSerializer

class UserApiAvatar(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    model = Lageruser
    serializer_class = UserAvatarSerializer

    def get_object(self, kwargs=None):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, username=self.kwargs["username"])
        self.check_object_permissions(self.request, obj)
        return obj

class IpAddressApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer

class IpAddressApiCreate(generics.CreateAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer

class IpAddressApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer