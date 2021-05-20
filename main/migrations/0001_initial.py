from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('column', models.CharField(max_length=1, choices=[('l', 'left'), ('r', 'right')])),
                ('index', models.IntegerField()),
                ('widgetname', models.CharField(max_length=200, choices=[('shorttermdevices', 'Devices for short term lending'), ('statistics', 'Statistics'), ('groups', 'Groups'), ('newestdevices', 'Newest devices'), ('edithistory', 'Edit history'), ('returnsoon', 'Devices, that are due soon'), ('bookmarks', 'Bookmarked Devices'), ('recentlendings', 'Recent lendings'), ('sections', 'Sections'), ('overdue', 'Overdue devices')])),
                ('minimized', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
