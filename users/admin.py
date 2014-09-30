from django.contrib import admin

from users.models import Lageruser, Department, DepartmentUser


admin.site.register(Lageruser)
admin.site.register(Department)
admin.site.register(DepartmentUser)