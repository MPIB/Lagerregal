# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-05 08:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0008_auto_20180924_1512'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='group',
            new_name='devicegroup',
        ),
    ]
