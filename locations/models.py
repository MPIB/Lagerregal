from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import reversion


class Section(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse('section-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('section-edit', kwargs={'pk': self.pk})


@reversion.register()
class Building(models.Model):
    name = models.CharField(_('Name'), max_length=200, unique=True)
    street = models.CharField(_('Street'), max_length=100, blank=True)
    number = models.CharField(_('Number'), max_length=30, blank=True)
    zipcode = models.CharField(_('ZIP code'), max_length=5, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    state = models.CharField(_('State'), max_length=100, blank=True)
    country = models.CharField(_('Country'), max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Building')
        verbose_name_plural = _('Buildings')
        ordering = ["name"]
        db_table = "devices_building"

    def get_absolute_url(self):
        return reverse('building-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('building-edit', kwargs={'pk': self.pk})


@reversion.register()
class Room(models.Model):
    name = models.CharField(_('Name'), max_length=200)
    building = models.ForeignKey(Building, null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name="rooms", blank=True)

    def __str__(self):
        if self.building:
            return self.name + " (" + str(self.building) + ")"
        else:
            return self.name

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        ordering = ["name"]
        db_table = "devices_room"

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('room-edit', kwargs={'pk': self.pk})