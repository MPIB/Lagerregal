from django.contrib import admin

from users.models import Lageruser, Department


admin.site.register(Lageruser)
admin.site.register(Department)