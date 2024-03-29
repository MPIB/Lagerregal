# Generated by Django 2.2.10 on 2020-03-01 14:13

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0009_rm_read_perm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='building',
            options={'ordering': ['name'], 'verbose_name': 'Building', 'verbose_name_plural': 'Buildings'},
        ),
        migrations.AlterModelOptions(
            name='manufacturer',
            options={'ordering': ['name'], 'verbose_name': 'Manufacturer', 'verbose_name_plural': 'Manufacturers'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['name'], 'verbose_name': 'Room', 'verbose_name_plural': 'Rooms'},
        ),
        migrations.AddField(
            model_name='device',
            name='data_provider',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
