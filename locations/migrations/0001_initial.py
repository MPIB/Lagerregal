from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Section',
                'verbose_name_plural': 'Sections',
                'permissions': (('read_section', 'Can read Section'),),
            },
        ),
    ]
