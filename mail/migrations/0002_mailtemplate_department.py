# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '__first__'),
        ('mail', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailtemplate',
            name='department',
            field=models.ForeignKey(to='users.Department', null=True),
            preserve_default=True,
        ),
    ]
