# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('devices', '__first__'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=500, verbose_name='Subject')),
                ('body', models.CharField(max_length=10000, verbose_name='Body')),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(to='devices.Device', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, verbose_name='Name')),
                ('subject', models.CharField(max_length=500, verbose_name='Subject')),
                ('body', models.CharField(max_length=10000, verbose_name='Body')),
                ('usage', models.CharField(null=True, choices=[(b'room', 'Room is changed'), (b'owner', 'person currently lending is changed'), (b'new', 'New Device is created'), (b'reminder', 'Reminder that device is still owned'), (b'trashed', 'Device is trashed'), (b'overdue', 'Reminder that device is overdue')], max_length=200, blank=True, unique=True, verbose_name='Usage')),
            ],
            options={
                'verbose_name': 'Mailtemplate',
                'verbose_name_plural': 'Mailtemplates',
                'permissions': (('read_mailtemplate', 'Can read Mailtemplate'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailTemplateRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('mailtemplate', models.ForeignKey(related_name=b'default_recipients', to='mail.MailTemplate')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='mailtemplate',
            field=models.ForeignKey(to='mail.MailTemplate'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='sent_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
