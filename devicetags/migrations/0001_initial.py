from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20151105_0513'),
    ]

    operations = [
        migrations.CreateModel(
            name='Devicetag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('devices', models.ManyToManyField(related_name='tags', to='devices.Device')),
            ],
            options={
                'verbose_name': 'Devicetag',
                'verbose_name_plural': 'Devicegtag',
                'permissions': (('read_devicetag', 'Can read Devicetag'),),
            },
        ),
    ]
