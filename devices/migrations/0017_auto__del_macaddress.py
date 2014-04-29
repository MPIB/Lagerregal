# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Deleting model 'MacAddress'
        db.delete_table('devices_macaddress')


    def backwards(self, orm):
        # Adding model 'MacAddress'
        db.create_table('devices_macaddress', (
            ('macaddress', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(related_name='macaddresses',
                                                                             to=orm['devices.Device'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('devices', ['MacAddress'])


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [],
                            {'symmetrical': 'False', 'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)",
                     'ordering': "('content_type__app_label', 'content_type__model', 'codename')",
                     'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': (
            'django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)",
                     'db_table': "'django_content_type'", 'object_name': 'ContentType'},
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        'devices.device': {
            'Meta': {'object_name': 'Device'},
            'archived': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'bookmarkers': ('django.db.models.fields.related.ManyToManyField', [],
                            {'symmetrical': 'False', 'to': "orm['users.Lageruser']", 'null': 'True',
                             'related_name': "'bookmarks'", 'through': "orm['devices.Bookmark']", 'blank': 'True'}),
            'created_at': (
            'django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'currentlending': ('django.db.models.fields.related.ForeignKey', [],
                               {'related_name': "'currentdevice'", 'to': "orm['devices.Lending']", 'null': 'True',
                                'blank': 'True', 'on_delete': 'models.SET_NULL'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [],
                           {'to': "orm['devicetypes.Type']", 'null': 'True', 'blank': 'True',
                            'on_delete': 'models.SET_NULL'}),
            'group': ('django.db.models.fields.related.ForeignKey', [],
                      {'related_name': "'devices'", 'to': "orm['devicegroups.Devicegroup']", 'null': 'True',
                       'blank': 'True', 'on_delete': 'models.SET_NULL'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventoried': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'inventorynumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [],
                             {'to': "orm['devices.Manufacturer']", 'null': 'True', 'blank': 'True',
                              'on_delete': 'models.SET_NULL'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'room': ('django.db.models.fields.related.ForeignKey', [],
                     {'to': "orm['devices.Room']", 'null': 'True', 'blank': 'True', 'on_delete': 'models.SET_NULL'}),
            'serialnumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'templending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trashed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'webinterface': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'})
        },
        'devices.deviceinformation': {
            'Meta': {'object_name': 'DeviceInformation'},
            'device': ('django.db.models.fields.related.ForeignKey', [],
                       {'related_name': "'information'", 'to': "orm['devices.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'infotype': (
            'django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.DeviceInformationType']"})
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
            'duedate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duedate_email': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lenddate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'returndate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'devices.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'devices.note': {
            'Meta': {'object_name': 'Note'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Lageruser']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [],
                       {'related_name': "'notes'", 'to': "orm['devices.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        'devices.room': {
            'Meta': {'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [],
                         {'to': "orm['devices.Building']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'section': ('django.db.models.fields.related.ForeignKey', [],
                        {'related_name': "'rooms'", 'to': "orm['locations.Section']", 'null': 'True',
                         'on_delete': 'models.SET_NULL'})
        },
        'devices.template': {
            'Meta': {'object_name': 'Template'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [],
                           {'to': "orm['devicetypes.Type']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [],
                             {'to': "orm['devices.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'templatename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'devicetypes.type': {
            'Meta': {'object_name': 'Type'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'locations.section': {
            'Meta': {'object_name': 'Section'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'users.lageruser': {
            'Meta': {'object_name': 'Lageruser'},
            'avatar': (
            'django.db.models.fields.files.ImageField', [], {'null': 'True', 'max_length': '100', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [],
                       {'related_name': "'user_set'", 'symmetrical': 'False', 'to': "orm['auth.Group']",
                        'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [],
                         {'default': "'de'", 'null': 'True', 'max_length': '10', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'pagelength': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('django.db.models.fields.CharField', [],
                         {'default': 'None', 'null': 'True', 'max_length': '50', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [],
                                 {'related_name': "'user_set'", 'symmetrical': 'False', 'to': "orm['auth.Permission']",
                                  'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['devices']