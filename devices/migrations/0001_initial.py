from django.db import migrations
from django.db import models

import Lagerregal.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
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
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'permissions': (('boss_mails', 'Emails for bosses'), ('managment_mails', 'Emails for managment'), ('support_mails', 'Emails for support'), ('read_device', 'Can read Device'), ('lend_device', 'Can lend Device')),
            },
        ),
        migrations.CreateModel(
            name='DeviceInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('information', models.CharField(max_length=200, verbose_name='Information')),
            ],
            options={
                'verbose_name': 'Information',
                'verbose_name_plural': 'Information',
            },
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
            ],
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
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.CharField(max_length=5000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=Lagerregal.utils.get_file_location)),
                ('caption', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Picture',
                'verbose_name_plural': 'Pictures',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
                'permissions': (('read_room', 'Can read Room'),),
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('templatename', models.CharField(max_length=200, verbose_name='Templatename')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', models.CharField(max_length=1000, verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'Template',
                'verbose_name_plural': 'Templates',
                'permissions': (('read_template', 'Can read Template'),),
            },
        ),
    ]
