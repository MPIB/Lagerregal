# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Lagerregal.utils


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=Lagerregal.utils.get_file_location)),
                ('caption', models.CharField(max_length=200)),
                ('device', models.ForeignKey(related_name='pictures', to='devices.Device')),
            ],
            options={
                'verbose_name': 'Picture',
                'verbose_name_plural': 'Pictures',
            },
            bases=(models.Model,),
        ),
    ]
