import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devices', '0002_auto_20151105_0513'),
        ('users', '0006_auto_20151105_0513'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=500, verbose_name='Subject')),
                ('body', models.CharField(max_length=10000, verbose_name='Body')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(to='devices.Device', null=True, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Name')),
                ('subject', models.CharField(max_length=500, verbose_name='Subject')),
                ('body', models.CharField(max_length=10000, verbose_name='Body')),
                ('usage', models.CharField(blank=True, max_length=200, null=True, verbose_name='Usage', choices=[('room', 'Room is changed'), ('owner', 'person currently lending is changed'), ('new', 'New Device is created'), ('reminder', 'Reminder that device is still owned'), ('trashed', 'Device is trashed'), ('overdue', 'Reminder that device is overdue')])),
                ('department', models.ForeignKey(to='users.Department', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Mailtemplate',
                'verbose_name_plural': 'Mailtemplates',
                'permissions': (('read_mailtemplate', 'Can read Mailtemplate'),),
            },
        ),
        migrations.CreateModel(
            name='MailTemplateRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', on_delete=models.CASCADE)),
                ('mailtemplate', models.ForeignKey(related_name='default_recipients', to='mail.MailTemplate', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='mailtemplate',
            field=models.ForeignKey(to='mail.MailTemplate', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='sent_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
