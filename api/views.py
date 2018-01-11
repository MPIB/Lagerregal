from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import rest_framework.reverse
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from reversion import revisions as reversion
import datetime
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse


from api.serializers import *
from devices.models import *
from devicetypes.models import *
from network.models import *
from django.contrib.auth.models import Group
from mail.models import MailTemplate

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
        'groups': rest_framework.reverse.reverse('group-api-list', request=request),
    })


class SearchQuerysetMixin():
    def get_queryset(self):
        queryset = self.model.objects.all()
        valid_fields = self.model._meta.fields
        filters = {}
        for param in self.request.query_params.lists():
            if param[0] in valid_fields:
                key_name = param[0] + "__in"
                if param[0] == "department":
                    key_name = "department__name__in"
                filters[key_name] = param[1]
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
    queryset = Device.objects.all()

    def get_object(self, query=None):
        if query:
            device = super(DeviceApiDetail, self).get_object(query)
        else:
            device = super(DeviceApiDetail, self).get_object()
        device.bookmarked = device.bookmarkers.filter(id=self.request.user.id).exists()
        return device

class DeviceApiRoomChange(generics.UpdateAPIView):
    model = Device
    queryset = Device.objects.all()
    serializer_class = DeviceRoomSerializer

    def post(self, request, pk):
        return self.put(request, pk)

    def put(self, request, pk, **kwargs):
        response = super(DeviceApiRoomChange, self).put(request, pk)
        try:
            template = MailTemplate.objects.get(usage="room")
        except:
            template = None
        if not template == None:
            recipients = []
            for recipient in template.default_recipients.all():
                recipient = recipient.content_object
                if isinstance(recipient, Group):
                    recipients += recipient.lageruser_set.all().values_list("email")[0]
                else:
                    recipients.append(recipient.email)
            template.send(self.request, recipients, {"device": self.get_object(), "user": self.request.user})

        reversion.set_user(request.user)
        reversion.set_comment(_("Device moved to room {0}").format(self.get_object().room))
        return response

class DeviceApiBookmark(APIView):
    def post(self, request, pk):
        try:
            device = Device.objects.get(pk=pk)
        except Device.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        if "bookmarked" in request.POST:
            if "note" in request.POST:
                if request.POST["note"] != "":
                    note = Note()
                    note.device = device
                    note.creator = request.user
                    note.note = request.POST["note"]
                    note.save()
            if request.POST["bookmarked"] and not device.bookmarkers.filter(id=request.user.id).exists():
                bookmark = Bookmark(device=device, user=request.user)
                bookmark.save()
                return Response({"success": "added bookmark"})
            elif not request.POST["bookmarked"] and device.bookmarkers.filter(id=request.user.id).exists():
                bookmark = Bookmark.objects.get(user=request.user, device=device)
                bookmark.delete()
                return Response({"success": "removed bookmark"})
            else:
                return Response({"success": "added note"})
        else:
            return Response({"error": "the 'bookmarked' argument is mandatory"}, status=status.HTTP_400_BAD_REQUEST)


class DeviceApiLend(generics.CreateAPIView):
    serializer_class = LendingSerializer

    def post(self, request, *args, **kwargs):
        if "room" in request.POST:
            if request.POST["room"] != "" and request.POST["room"] != 0:
                roomid = request.POST["room"][0]
                room = get_object_or_404(Room, pk=roomid)
            else:
                room = None
        else:
            room = None
        response = super(DeviceApiLend, self).post(request)
        if request.POST["device"] != "" and response.status_code == 201:
            device = Device.objects.get(pk=request.POST["device"])
            device.currentlending = self.object
            if room:
                device.room = room
                reversion.set_user(request.user)
                reversion.set_comment("Device marked as lend")
                try:
                    template = MailTemplate.objects.get(usage="room")
                except:
                    template = None
                if not template == None:
                    recipients = []
                    for recipient in template.default_recipients.all():
                        recipient = recipient.content_object
                        if isinstance(recipient, Group):
                            recipients += recipient.lageruser_set.all().values_list("email")[0]
                        else:
                            recipients.append(recipient.email)
                    template.send(self.request, recipients, {"device": device, "user": self.request.user})
            reversion.set_ignore_duplicates(True)
            device.save()
        return response

class DeviceApiReturn(APIView):

    def post(self, request, *args, **kwargs):
        if not "lending" in request.DATA:
            return Response({"error": "you need to provide a valid lending id"}, status=status.HTTP_400_BAD_REQUEST)
        if "room" in request.DATA:
            if request.DATA["room"] != "" and request.DATA["room"] != 0:
                roomid = request.DATA["room"]
                room = get_object_or_404(Room, pk=roomid)
            else:
                room = None
        else:
            room = None

        lending = get_object_or_404(Lending, pk=request.DATA["lending"])
        if lending.device and lending.device != "":
            device = lending.device
            device.currentlending = None
            if room:
                device.room = room
                reversion.set_user(request.user)
                try:
                    template = MailTemplate.objects.get(usage="room")
                except:
                    template = None
                if not template == None:
                    recipients = []
                    for recipient in template.default_recipients.all():
                        recipient = recipient.content_object
                        if isinstance(recipient, Group):
                            recipients += recipient.lageruser_set.all().values_list("email")[0]
                        else:
                            recipients.append(recipient.email)
                    template.send(self.request, recipients, {"device": device, "user": self.request.user})
                reversion.set_comment(_("Device returned and moved to room {0}").format(device.room))
            device.save()
        else:
            pass

        lending.returndate = datetime.datetime.now()
        lending.save()

        return Response({"success": "device is returned"}, status=status.HTTP_200_OK)


class DeviceApiListPictures(generics.ListCreateAPIView):
    model = Picture
    serializer_class = PictureSerializer

    def get_queryset(self):
        return Picture.objects.filter(device__pk=self.kwargs["pk"])

    def create(self, request, *args, **kwargs):
        serializer = PictureSerializer(data=request.data)
        device = get_object_or_404(Device, pk=kwargs["pk"])
        if serializer.is_valid():
            serializer.validated_data["device"] = device
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class DeviceApiPicture(generics.RetrieveDestroyAPIView):
    model = Picture
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

class DeviceApiPictureRotate(generics.RetrieveUpdateAPIView):
    model = Picture
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def patch(self, request, *args, **kwargs):
        from PIL import Image
        import StringIO
        from django.core.files.uploadedfile import InMemoryUploadedFile


        picture = get_object_or_404(Picture, pk=self.kwargs["pk"])
        img = Image.open(picture.image)
        #determine if orientation is left or right
        if self.kwargs["orientation"] == "right":
            img  = img.transpose(Image.ROTATE_270)
        if self.kwargs["orientation"] == "left":
            img  = img.transpose(Image.ROTATE_90)
        img.save(picture.image.file.name)
        img.close()
        return HttpResponse(status=200, content_type='text/html')



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

class UserApiProfile(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserApiAvatar(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    model = Lageruser
    serializer_class = UserAvatarSerializer
    queryset = Lageruser.objects.all()

    def get_object(self, kwargs=None):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, username=self.kwargs["username"])
        self.check_object_permissions(self.request, obj)
        return obj

class GroupApiList(SearchQuerysetMixin, generics.ListAPIView):
    model = Group
    serializer_class = GroupSerializer


class GroupApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Group
    serializer_class = GroupSerializer

class IpAddressApiList(SearchQuerysetMixin, generics.ListCreateAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer


class IpAddressApiCreate(generics.CreateAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer


class IpAddressApiDetail(generics.RetrieveUpdateDestroyAPIView):
    model = IpAddress
    serializer_class = IpAddressSerializer


class SmallDeviceApiList(APIView):
    def get(self, request, subpart=None):
        smalldevices = Lending.objects.exclude(smalldevice=None).exclude(smalldevice="")
        if subpart:
            smalldevices = smalldevices.filter(smalldevice__icontains=subpart)
        smalldevices = smalldevices.values_list("smalldevice").distinct()
        smalldevices = [smalldevice[0] for smalldevice in smalldevices]
        return Response(smalldevices, status=status.HTTP_200_OK)
