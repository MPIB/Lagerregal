# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150526_0403'),
    ]

    operations = [
        migrations.CreateModel(
            name='Devicegroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Devicegroup',
                'verbose_name_plural': 'Devicegroups',
                'permissions': (('read_devicegroup', 'Can read Devicegroup'),),
            },
        ),
    ]
