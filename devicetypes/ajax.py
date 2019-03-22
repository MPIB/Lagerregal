# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import HttpResponse
from django.views.generic.base import View

from devicetypes.models import TypeAttribute


class GetTypeAttributes(View):

    def get(self, request):
        pk = request.GET.get("pk", "")

        if not pk == "":
            attributes = TypeAttribute.objects.filter(devicetype__pk=pk)
            data = []

            for attribute in attributes:
                data.append({
                    "id": attribute.pk,
                    "name": attribute.name
                })

            return HttpResponse(json.dumps(data), content_type='application/json')

        return HttpResponse("")
