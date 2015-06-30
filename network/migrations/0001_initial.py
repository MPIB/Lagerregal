# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devices', '0003_auto_20150610_0653'),
        ('users', '0005_auto_20150526_0403'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.IPAddressField(unique=True)),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('purpose', models.CharField(max_length=200, null=True, blank=True)),
                ('department', models.ForeignKey(blank=True, to='users.Department', null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Device', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'IP-Address',
                'verbose_name_plural': 'IP-Addresses',
                'permissions': (('read_ipaddress', 'Can read IP-Address'),),
            },
        ),
    ]
