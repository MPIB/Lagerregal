# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-31 07:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0011_auto_20180730_1057'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='servicetag',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]