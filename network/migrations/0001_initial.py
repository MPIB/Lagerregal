import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20151105_0513'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0006_auto_20151105_0513'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.GenericIPAddressField(unique=True)),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('purpose', models.CharField(max_length=200, null=True, blank=True)),
                ('department', models.ForeignKey(blank=True, to='users.Department', null=True, on_delete=models.CASCADE)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Device', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'IP-Address',
                'verbose_name_plural': 'IP-Addresses',
                'permissions': (('read_ipaddress', 'Can read IP-Address'),),
            },
        ),
    ]
