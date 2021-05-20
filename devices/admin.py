from django.contrib import admin

from devices.models import Building
from devices.models import Device
from devices.models import DeviceInformation
from devices.models import DeviceInformationType
from devices.models import Lending
from devices.models import Manufacturer
from devices.models import Note
from devices.models import Picture
from devices.models import Room
from devices.models import Template


class DeviceAdmin(admin.ModelAdmin):
    # List display
    list_display = ('name',)


admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Manufacturer)
admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceInformationType)
admin.site.register(DeviceInformation)
admin.site.register(Lending)
admin.site.register(Template)
admin.site.register(Note)
admin.site.register(Picture)
