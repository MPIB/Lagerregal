from django.contrib import admin

from users.models import Lageruser, Department, DepartmentUser

class LageruserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', )

admin.site.register(Lageruser, LageruserAdmin)
admin.site.register(Department)
admin.site.register(DepartmentUser)
