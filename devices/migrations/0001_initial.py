# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('devicetypes', '__first__'),
        ('devicegroups', '__first__'),
        ('locations', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_auto_20150129_0422'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Name')),
                ('street', models.CharField(max_length=100, verbose_name='Street', blank=True)),
                ('number', models.CharField(max_length=30, verbose_name='Number', blank=True)),
                ('zipcode', models.CharField(max_length=5, verbose_name='ZIP code', blank=True)),
                ('city', models.CharField(max_length=100, verbose_name='City', blank=True)),
                ('state', models.CharField(max_length=100, verbose_name='State', blank=True)),
                ('country', models.CharField(max_length=100, verbose_name='Country', blank=True)),
            ],
            options={
                'verbose_name': 'Building',
                'verbose_name_plural': 'Buildings',
                'permissions': (('read_building', 'Can read Building'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('inventorynumber', models.CharField(max_length=50, verbose_name='Inventorynumber', blank=True)),
                ('serialnumber', models.CharField(max_length=50, verbose_name='Serialnumber', blank=True)),
                ('hostname', models.CharField(max_length=40, verbose_name='Hostname', blank=True)),
                ('description', models.CharField(max_length=10000, verbose_name='Description', blank=True)),
                ('webinterface', models.CharField(max_length=60, verbose_name='Webinterface', blank=True)),
                ('templending', models.BooleanField(default=False, verbose_name='For short term lending')),
                ('archived', models.DateTimeField(null=True, blank=True)),
                ('trashed', models.DateTimeField(null=True, blank=True)),
                ('inventoried', models.DateTimeField(null=True, blank=True)),
                ('is_private', models.BooleanField(default=False)),
                ('bookmarkers', models.ManyToManyField(related_name='bookmarks', null=True, through='devices.Bookmark', to=settings.AUTH_USER_MODEL, blank=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'permissions': (('boss_mails', 'Emails for bosses'), ('managment_mails', 'Emails for managment'), ('support_mails', 'Emails for support'), ('read_device', 'Can read Device'), ('lend_device', 'Can lend Device')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeviceInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('information', models.CharField(max_length=200, verbose_name='Information')),
                ('device', models.ForeignKey(related_name='information', to='devices.Device')),
            ],
            options={
                'verbose_name': 'Information',
                'verbose_name_plural': 'Information',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeviceInformationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyname', models.CharField(max_length=200, verbose_name='Name')),
                ('humanname', models.CharField(max_length=200, verbose_name='Human readable name')),
            ],
            options={
                'verbose_name': 'Information Type',
                'verbose_name_plural': 'Information Type',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lending',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lenddate', models.DateField(auto_now_add=True)),
                ('duedate', models.DateField(null=True, blank=True)),
                ('duedate_email', models.DateField(null=True, blank=True)),
                ('returndate', models.DateField(null=True, blank=True)),
                ('smalldevice', models.CharField(max_length=200, null=True, verbose_name='Small Device', blank=True)),
                ('device', models.ForeignKey(blank=True, to='devices.Device', null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Lent to', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Manufacturer')),
            ],
            options={
                'verbose_name': 'Manufacturer',
                'verbose_name_plural': 'Manufacturers',
                'permissions': (('read_manufacturer', 'Can read Manufacturer'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.CharField(max_length=5000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('device', models.ForeignKey(related_name='notes', to='devices.Device')),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='devices.Building', null=True)),
                ('section', models.ForeignKey(related_name='rooms', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='locations.Section', null=True)),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
                'permissions': (('read_room', 'Can read Room'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('templatename', models.CharField(max_length=200, verbose_name='Templatename')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', models.CharField(max_length=1000, verbose_name='Description', blank=True)),
                ('devicetype', models.ForeignKey(blank=True, to='devicetypes.Type', null=True)),
                ('manufacturer', models.ForeignKey(blank=True, to='devices.Manufacturer', null=True)),
            ],
            options={
                'verbose_name': 'Template',
                'verbose_name_plural': 'Templates',
                'permissions': (('read_template', 'Can read Template'),),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deviceinformation',
            name='infotype',
            field=models.ForeignKey(to='devices.DeviceInformationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='currentlending',
            field=models.ForeignKey(related_name='currentdevice', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Lending', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='department',
            field=models.ForeignKey(related_name='devices', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='users.Department', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='devicetype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devicetypes.Type', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='group',
            field=models.ForeignKey(related_name='devices', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devicegroups.Devicegroup', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Manufacturer', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Room', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookmark',
            name='device',
            field=models.ForeignKey(to='devices.Device'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
