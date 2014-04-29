# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Lending.smalldevice'
        db.add_column('devices_lending', 'smalldevice',
                      self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True),
                      keep_default=False)


        # Changing field 'Lending.device'
        db.alter_column('devices_lending', 'device_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['devices.Device']))

    def backwards(self, orm):
        # Deleting field 'Lending.smalldevice'
        db.delete_column('devices_lending', 'smalldevice')


        # User chose to not deal with backwards NULL issues for 'Lending.device'
        raise RuntimeError("Cannot reverse this migration. 'Lending.device' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Lending.device'
        db.alter_column('devices_lending', 'device_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Device']))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
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
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        'devices.device': {
            'Meta': {'object_name': 'Device'},
            'archived': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'bookmarkers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bookmarks'", 'null': 'True', 'through': "orm['devices.Bookmark']", 'to': "orm['users.Lageruser']", 'symmetrical': 'False', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'currentlending': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'currentdevice'", 'on_delete': 'models.SET_NULL', 'null': 'True', 'blank': 'True', 'to': "orm['devices.Lending']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'blank': 'True', 'to': "orm['devicetypes.Type']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'devices'", 'on_delete': 'models.SET_NULL', 'null': 'True', 'blank': 'True', 'to': "orm['devicegroups.Devicegroup']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventoried': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'inventorynumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'blank': 'True', 'to': "orm['devices.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'blank': 'True', 'to': "orm['devices.Room']"}),
            'serialnumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'templending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trashed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'webinterface': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'})
        },
        'devices.deviceinformation': {
            'Meta': {'object_name': 'DeviceInformation'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'information'", 'to': "orm['devices.Device']"}),
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
            'device': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['devices.Device']"}),
            'duedate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duedate_email': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lenddate': ('django.db.models.fields.DateField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'returndate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'smalldevice': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'devices.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'})
        },
        'devices.note': {
            'Meta': {'object_name': 'Note'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': "orm['devices.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        'devices.room': {
            'Meta': {'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['devices.Building']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rooms'", 'on_delete': 'models.SET_NULL', 'null': 'True', 'to': "orm['locations.Section']"})
        },
        'devices.template': {
            'Meta': {'object_name': 'Template'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['devicetypes.Type']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['devices.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'templatename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'devicetypes.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True'})
        },
        'locations.section': {
            'Meta': {'object_name': 'Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'users.lageruser': {
            'Meta': {'object_name': 'Lageruser'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10', 'default': "'de'", 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'pagelength': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': 'None', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        }
    }

    complete_apps = ['devices']