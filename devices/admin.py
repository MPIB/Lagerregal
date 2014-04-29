from django.contrib import admin

from devices.models import *


class DeviceAdmin(admin.ModelAdmin):

    # List display
    list_display = ('name',)

admin.site.register(Device, DeviceAdmin)

admin.site.register(Type)
admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Manufacturer)