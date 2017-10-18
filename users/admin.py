from django.contrib import admin

from users.models import Lageruser, Department, DepartmentUser

class LageruserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', )

class DepartmentUserAdmin(admin.ModelAdmin):
    search_fields = ('user__first_name', 'user__last_name', )

admin.site.register(Lageruser, LageruserAdmin)
admin.site.register(DepartmentUser, DepartmentUserAdmin)
admin.site.register(Department)
