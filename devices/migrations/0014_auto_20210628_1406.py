# Generated by Django 3.2.3 on 2021-06-28 12:06

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_building_room'),
        ('devices', '0013_auto_20200509_1148'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='room',
                    name='building',
                ),
                migrations.RemoveField(
                    model_name='room',
                    name='section',
                )
            ],
            database_operations=[],
        ),
        migrations.AlterField(
            model_name='device',
            name='operating_system',
            field=models.CharField(blank=True, choices=[('win', 'Windows'), ('osx', 'macOS'), ('linux', 'Linux')], max_length=10, null=True),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='device',
                    name='room',
                    field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.Room'),
                ),
                migrations.DeleteModel(
                    name='Building',
                ),
                migrations.DeleteModel(
                    name='Room',
                )
            ],
            database_operations=[],
        ),
    ]
