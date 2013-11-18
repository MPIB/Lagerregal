# -*- coding: utf-8 -*-
from south.db import db

class Migration:

    def forwards(self, orm):
        # Rename 'name' field to 'full_name'
        db.rename_column('devices_device', 'bildnumber', 'inventorynumber')




    def backwards(self, orm):
        # Rename 'full_name' field to 'name'
        db.rename_column('devices_device', 'inventorynumber', 'bildnumber')