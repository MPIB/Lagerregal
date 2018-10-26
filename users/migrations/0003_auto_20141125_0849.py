# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_lageruser_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lageruser',
            name='expiration_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
