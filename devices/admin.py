from django.contrib import admin

from devices.models import *


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
