# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150526_0403'),
        ('devicegroups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicegroup',
            name='department',
            field=models.ForeignKey(to='users.Department', null=True),
        ),
    ]
