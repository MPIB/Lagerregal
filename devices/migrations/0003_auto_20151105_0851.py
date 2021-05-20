import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models

import Lagerregal.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devices', '0002_auto_20151105_0513'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='contact',
            field=models.ForeignKey(related_name='as_contact', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, help_text='Person to contact about using this device', null=True),
        ),
        migrations.AddField(
            model_name='device',
            name='manual',
            field=models.FileField(null=True, upload_to=Lagerregal.utils.get_file_location, blank=True),
        ),
    ]
