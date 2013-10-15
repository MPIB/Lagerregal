from devices.models import *
from django.contrib import admin
class DeviceAdmin(admin.ModelAdmin):

    # List display
    list_display = ('name',)

admin.site.register(Device, DeviceAdmin)

admin.site.register(Type)
admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Manufacturer)