# Generated by Django 2.2.12 on 2020-05-25 16:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('devices', '0013_auto_20200509_1148'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProvidedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stored_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('raw_value', models.CharField(max_length=2000)),
                ('formatted_value', models.CharField(max_length=500)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provided_data', to='devices.Device')),
            ],
        ),
    ]
