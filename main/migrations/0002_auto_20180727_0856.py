# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-27 06:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardwidget',
            name='column',
            field=models.CharField(choices=[('l', 'left'), ('r', 'right')], max_length=1),
        ),
        migrations.AlterField(
            model_name='dashboardwidget',
            name='widgetname',
            field=models.CharField(choices=[('edithistory', 'Edit history'), ('newestdevices', 'Newest devices'), ('overdue', 'Overdue devices'), ('statistics', 'Statistics'), ('groups', 'Groups'), ('sections', 'Sections'), ('recentlendings', 'Recent lendings'), ('shorttermdevices', 'Devices for short term lending'), ('bookmarks', 'Bookmarked Devices'), ('returnsoon', 'Devices, that are due soon')], max_length=200),
        ),
    ]
