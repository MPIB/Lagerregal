from api.serializers import DeviceSerializer, DeviceListSerializer, TypeSerializer, RoomSerializer, BuildingSerializer, ManufacturerSerializer, TemplateSerializer
from devices.models import *
from devicetypes.models import *
from network.models import *
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
import rest_framework.reverse

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


class DeviceApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = Device
    serializer_class = DeviceListSerializer

class DeviceApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Device
    serializer_class = DeviceSerializer


class TypeApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = Type
    serializer_class = TypeSerializer

class TypeApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Type
    serializer_class = TypeSerializer       


class RoomApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = Room
    serializer_class = RoomSerializer

class RoomApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Room
    serializer_class = RoomSerializer


class BuildingApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = Building
    serializer_class = BuildingSerializer

class BuildingApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Building
    serializer_class = BuildingSerializer


class ManufacturerApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = Manufacturer
    serializer_class = ManufacturerSerializer

class ManufacturerApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Manufacturer
    serializer_class = ManufacturerSerializer


class TemplateApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = Template
    serializer_class = TemplateSerializer

class TemplateApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Template
    serializer_class = TemplateSerializer
