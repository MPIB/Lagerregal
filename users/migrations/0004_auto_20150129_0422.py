# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Lagerregal.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20141125_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lageruser',
            name='avatar',
            field=models.ImageField(null=True, upload_to=Lagerregal.utils.get_file_location, blank=True),
            preserve_default=True,
        ),
    ]
