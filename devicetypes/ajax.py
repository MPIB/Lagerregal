# -*- coding: utf-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from devices.models import Device, Room, Building, Manufacturer
from devicetypes.models import TypeAttribute
from django.utils import simplejson
from django.core.urlresolvers import reverse

@dajaxice_register
def get_attributes(request, pk):
    dajax = Dajax()
    attributes = TypeAttribute.objects.filter(devicetype__pk = pk )
    dajax.clear("#extra_attributes", "innerHTML")
    for attribute in attributes:
        item = u"""<div class="row">
        <div class="small-3 columns">
          <label for="right-label" class="right inline">{0}</label>
        </div>
        <div class="small-9 columns">
        <input type="text" id="id_attribute_{1}" name="attribute_{1}" />
        </div>
      </div>
        """.format(attribute.name, attribute.pk)
        dajax.append("#extra_attributes", "innerHTML", item)

    return dajax.json()