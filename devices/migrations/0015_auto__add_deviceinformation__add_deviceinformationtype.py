# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DeviceInformation'
        db.create_table('devices_deviceinformation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('information', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Device'], related_name='information')),
            ('infotype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.DeviceInformationType'])),
        ))
        db.send_create_signal('devices', ['DeviceInformation'])

        # Adding model 'DeviceInformationType'
        db.create_table('devices_deviceinformationtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyname', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('humanname', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('devices', ['DeviceInformationType'])


    def backwards(self, orm):
        # Deleting model 'DeviceInformation'
        db.delete_table('devices_deviceinformation')

        # Deleting model 'DeviceInformationType'
        db.delete_table('devices_deviceinformationtype')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)", 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'devicegroups.devicegroup': {
            'Meta': {'object_name': 'Devicegroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'devices.bookmark': {
            'Meta': {'object_name': 'Bookmark'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"})
        },
        'devices.building': {
            'Meta': {'object_name': 'Building'},
            'city': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'number': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'street': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '5'})
        },
        'devices.device': {
            'Meta': {'object_name': 'Device'},
            'archived': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'bookmarkers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'through': "orm['devices.Bookmark']", 'to': "orm['users.Lageruser']", 'symmetrical': 'False', 'null': 'True', 'related_name': "'bookmarks'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True', 'auto_now_add': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'currentlending': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devices.Lending']", 'related_name': "'currentdevice'"}),
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '10000'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devicetypes.Type']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devicegroups.Devicegroup']", 'related_name': "'devices'"}),
            'hostname': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventoried': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'inventorynumber': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '50'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devices.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devices.Room']"}),
            'serialnumber': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '50'}),
            'templending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trashed': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'webinterface': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '60'})
        },
        'devices.deviceinformation': {
            'Meta': {'object_name': 'DeviceInformation'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']", 'related_name': "'information'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'infotype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.DeviceInformationType']"})
        },
        'devices.deviceinformationtype': {
            'Meta': {'object_name': 'DeviceInformationType'},
            'humanname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyname': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'devices.lending': {
            'Meta': {'object_name': 'Lending'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']"}),
            'duedate': ('django.db.models.fields.DateField', [], {'blank': 'True', 'null': 'True'}),
            'duedate_email': ('django.db.models.fields.DateField', [], {'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lenddate': ('django.db.models.fields.DateField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'returndate': ('django.db.models.fields.DateField', [], {'blank': 'True', 'null': 'True'})
        },
        'devices.macaddress': {
            'Meta': {'object_name': 'MacAddress'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']", 'related_name': "'macaddresses'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'macaddress': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        'devices.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'devices.note': {
            'Meta': {'object_name': 'Note'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']", 'related_name': "'notes'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        'devices.room': {
            'Meta': {'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devices.Building']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'devices.template': {
            'Meta': {'object_name': 'Template'},
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '1000'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['devicetypes.Type']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['devices.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'templatename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'devicetypes.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'users.lageruser': {
            'Meta': {'object_name': 'Lageruser'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'blank': 'True', 'max_length': '100', 'null': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Group']", 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '10', 'null': 'True', 'default': "'de'"}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'pagelength': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '50', 'null': 'True', 'default': 'None'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['devices']