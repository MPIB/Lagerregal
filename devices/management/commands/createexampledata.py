# -*- coding: utf-8 -*-
from django.conf import settings  # import the settings file
from django.core.management.base import BaseCommand

from users.models import Lageruser
from locations.models import Section
from devices.models import Building, Room, Device, Manufacturer, Lending
from devicetypes.models import Type
from devicegroups.models import Devicegroup

from datetime import date, timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        err = SystemExit('refused to create example objects outside of demo mode')
        try:
            if not settings.DEMO_MODE:
                raise err
        except AttributeError as e:
            raise err
        Lageruser.objects.create_superuser('admin', 'admin@localhost', 'admin')
        Section.objects.create(name='Headquarters')
        Building.objects.create(name='Hall A')
        Room.objects.create(name='23', building=Building.objects.first(),
                            section=Section.objects.first())
        Room.objects.create(name='24', building=Building.objects.first(),
                            section=Section.objects.first())

        Manufacturer.objects.create(name='Apple')
        Devicegroup.objects.create(name='Human Resources')
        Type.objects.create(name='Notebook')
        device = Device(name='MacBook Pro 15 with Retina (mid-2015)',
                        room=Room.objects.first(),
                        devicetype=Type.objects.first(),
                        manufacturer=Manufacturer.objects.first(),
                        serialnumber='C02VK000000',
                        inventorynumber='4117')
        device.save()

        Lending.objects.create(owner=Lageruser.objects.first(),
                               device=Device.objects.first(),
                               duedate=date.today() + timedelta(days=1))
        device.currentlending = Lending.objects.first()
        device.save()
