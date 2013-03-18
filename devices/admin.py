from django.utils.translation import ugettext_lazy as _
from devices.models import *
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.comments.moderation import CommentModerator, moderator
import reversion
class DeviceAdmin(reversion.VersionAdmin):

	# List display
	list_display = ('name',)

admin.site.register(Device, DeviceAdmin)

admin.site.register(Type)
admin.site.register(Building)
admin.site.register(Room)
admin.site.register(Manufacturer)