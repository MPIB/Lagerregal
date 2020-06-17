from django.db import models
from devices.models import Device


class ProvidedData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="provided_data")

    type = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    raw_value = models.CharField(max_length=2000)
    formatted_value = models.CharField(max_length=500)
    stored_at = models.DateTimeField(auto_now_add=True)
