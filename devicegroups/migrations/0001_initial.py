# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Devicegroup'
        db.create_table(u'devicegroups_devicegroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'devicegroups', ['Devicegroup'])


    def backwards(self, orm):
        # Deleting model 'Devicegroup'
        db.delete_table(u'devicegroups_devicegroup')


    models = {
        u'devicegroups.devicegroup': {
            'Meta': {'object_name': 'Devicegroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['devicegroups']