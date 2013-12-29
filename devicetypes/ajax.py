# -*- coding: utf-8 -*-
from devices.models import Device, Room, Building, Manufacturer
from devicetypes.models import TypeAttribute
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic.base import View

class GetTypeAttributes(View):
    def post(self, request):
        pk = request.POST.get("pk", "")
        if not pk == "":
            attributes = TypeAttribute.objects.filter(devicetype__pk = pk )
            data = []
            for attribute in attributes:
                data.append({
                    "id":attribute.pk,
                    "name":attribute.name
                    })
            return HttpResponse(simplejson.dumps(data), content_type='application/json')
        return HttpResponse("")