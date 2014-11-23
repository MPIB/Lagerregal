# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0002_mailtemplate_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailtemplate',
            name='usage',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Usage', choices=[(b'room', 'Room is changed'), (b'owner', 'person currently lending is changed'), (b'new', 'New Device is created'), (b'reminder', 'Reminder that device is still owned'), (b'trashed', 'Device is trashed'), (b'overdue', 'Reminder that device is overdue')]),
        ),
    ]
