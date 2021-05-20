from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Type',
                'verbose_name_plural': 'Types',
                'permissions': (('read_type', 'Can read Type'),),
            },
        ),
        migrations.CreateModel(
            name='TypeAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('regex', models.CharField(max_length=500, null=True, blank=True)),
                ('devicetype', models.ForeignKey(to='devicetypes.Type', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Type-attribute',
                'verbose_name_plural': 'Type-attributes',
            },
        ),
        migrations.CreateModel(
            name='TypeAttributeValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=400)),
                ('device', models.ForeignKey(to='devices.Device', on_delete=models.CASCADE)),
                ('typeattribute', models.ForeignKey(to='devicetypes.TypeAttribute', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Type-attribute value',
                'verbose_name_plural': 'Type-attribute values',
            },
        ),
    ]
