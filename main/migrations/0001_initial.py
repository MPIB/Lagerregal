# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('column', models.CharField(max_length=1, choices=[(b'l', b'left'), (b'r', b'right')])),
                ('index', models.IntegerField()),
                ('widgetname', models.CharField(max_length=200, choices=[(b'shorttermdevices', 'Devices for short term lending'), (b'statistics', 'Statistics'), (b'groups', 'Groups'), (b'newestdevices', 'Newest devices'), (b'edithistory', 'Edit history'), (b'returnsoon', 'Devices, that are due soon'), (b'bookmarks', 'Bookmarked Devices'), (b'recentlendings', 'Recent lendings'), (b'sections', 'Sections'), (b'overdue', 'Overdue devices')])),
                ('minimized', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
