# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Room.section'
        db.add_column(u'devices_room', 'section',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['locations.Section'], null=True, on_delete=models.SET_NULL),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Room.section'
        db.delete_column(u'devices_room', 'section_id')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'devicegroups.devicegroup': {
            'Meta': {'object_name': 'Devicegroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'devices.bookmark': {
            'Meta': {'object_name': 'Bookmark'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Lageruser']"})
        },
        u'devices.building': {
            'Meta': {'object_name': 'Building'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
        u'devices.device': {
            'Meta': {'object_name': 'Device'},
            'archived': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'bookmarkers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'bookmarks'", 'to': u"orm['users.Lageruser']", 'through': u"orm['devices.Bookmark']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Lageruser']"}),
            'currentlending': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'currentdevice'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['devices.Lending']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devicetypes.Type']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'devices'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['devicegroups.Devicegroup']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inventoried': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'inventorynumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Manufacturer']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Room']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'serialnumber': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'templending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trashed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'webinterface': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'})
        },
        u'devices.lending': {
            'Meta': {'object_name': 'Lending'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Device']"}),
            'duedate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duedate_email': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lenddate': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Lageruser']"}),
            'returndate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'devices.macaddress': {
            'Meta': {'object_name': 'MacAddress'},
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'macaddresses'", 'to': u"orm['devices.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'macaddress': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'devices.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'devices.note': {
            'Meta': {'object_name': 'Note'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Lageruser']"}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notes'", 'to': u"orm['devices.Device']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        u'devices.room': {
            'Meta': {'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Building']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['locations.Section']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'devices.template': {
            'Meta': {'object_name': 'Template'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devicetypes.Type']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'templatename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'devicetypes.type': {
            'Meta': {'object_name': 'Type'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'locations.section': {
            'Meta': {'object_name': 'Section'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'users.lageruser': {
            'Meta': {'object_name': 'Lageruser'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'de'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'pagelength': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['devices']