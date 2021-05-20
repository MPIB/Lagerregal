from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20151105_0513'),
    ]

    operations = [
        migrations.CreateModel(
            name='Devicegroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('department', models.ForeignKey(to='users.Department', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Devicegroup',
                'verbose_name_plural': 'Devicegroups',
                'permissions': (('read_devicegroup', 'Can read Devicegroup'),),
            },
        ),
    ]
