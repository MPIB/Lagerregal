# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Building'
        db.create_table(u'devices_building', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=5, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'devices', ['Building'])

        # Adding model 'Room'
        db.create_table(u'devices_room', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Building'], null=True)),
        ))
        db.send_create_signal(u'devices', ['Room'])

        # Adding model 'Manufacturer'
        db.create_table(u'devices_manufacturer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'devices', ['Manufacturer'])

        # Adding model 'Device'
        db.create_table(u'devices_device', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Lageruser'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('bildnumber', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('serialnumber', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('macaddress', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Manufacturer'], null=True, blank=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('devicetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devicetypes.Type'], null=True, blank=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Room'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='devices', null=True, to=orm['devicegroups.Devicegroup'])),
            ('webinterface', self.gf('django.db.models.fields.CharField')(max_length=60, blank=True)),
            ('templending', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('currentlending', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='currentdevice', null=True, to=orm['devices.Lending'])),
            ('archived', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal(u'devices', ['Device'])

        # Adding model 'Lending'
        db.create_table(u'devices_lending', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.Lageruser'])),
            ('lenddate', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('duedate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('duedate_email', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('returndate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Device'])),
        ))
        db.send_create_signal(u'devices', ['Lending'])

        # Adding model 'Template'
        db.create_table(u'devices_template', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('templatename', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Manufacturer'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('devicetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devicetypes.Type'], null=True, blank=True)),
        ))
        db.send_create_signal(u'devices', ['Template'])


    def backwards(self, orm):
        # Deleting model 'Building'
        db.delete_table(u'devices_building')

        # Deleting model 'Room'
        db.delete_table(u'devices_room')

        # Deleting model 'Manufacturer'
        db.delete_table(u'devices_manufacturer')

        # Deleting model 'Device'
        db.delete_table(u'devices_device')

        # Deleting model 'Lending'
        db.delete_table(u'devices_lending')

        # Deleting model 'Template'
        db.delete_table(u'devices_template')


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
            'archived': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'bildnumber': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.Lageruser']"}),
            'currentlending': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'currentdevice'", 'null': 'True', 'to': u"orm['devices.Lending']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'devicetype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devicetypes.Type']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'devices'", 'null': 'True', 'to': u"orm['devicegroups.Devicegroup']"}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'macaddress': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Manufacturer']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Room']", 'null': 'True', 'blank': 'True'}),
            'serialnumber': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'templending': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        u'devices.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'devices.room': {
            'Meta': {'object_name': 'Room'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.Building']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
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
        u'users.lageruser': {
            'Meta': {'object_name': 'Lageruser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'de'", 'max_length': '10', 'null': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'pagelength': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['devices']