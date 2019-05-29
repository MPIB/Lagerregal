import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20151105_0513'),
        ('devices', '0001_initial'),
        ('devicetypes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devicegroups', '0001_initial'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='devicetype',
            field=models.ForeignKey(blank=True, to='devicetypes.Type', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='template',
            name='manufacturer',
            field=models.ForeignKey(blank=True, to='devices.Manufacturer', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='room',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='devices.Building', null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='section',
            field=models.ForeignKey(related_name='rooms', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='locations.Section', null=True),
        ),
        migrations.AddField(
            model_name='picture',
            name='device',
            field=models.ForeignKey(related_name='pictures', to='devices.Device', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='note',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='note',
            name='device',
            field=models.ForeignKey(related_name='notes', to='devices.Device', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='lending',
            name='device',
            field=models.ForeignKey(blank=True, to='devices.Device', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='lending',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Lent to', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='deviceinformation',
            name='device',
            field=models.ForeignKey(related_name='information', to='devices.Device', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='deviceinformation',
            name='infotype',
            field=models.ForeignKey(to='devices.DeviceInformationType', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='device',
            name='bookmarkers',
            field=models.ManyToManyField(related_name='bookmarks', null=True, through='devices.Bookmark', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='device',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='currentlending',
            field=models.ForeignKey(related_name='currentdevice', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Lending', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='department',
            field=models.ForeignKey(related_name='devices', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='users.Department', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='devicetype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devicetypes.Type', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='group',
            field=models.ForeignKey(related_name='devices', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devicegroups.Devicegroup', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='manufacturer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Manufacturer', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='devices.Room', null=True),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='device',
            field=models.ForeignKey(to='devices.Device', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
