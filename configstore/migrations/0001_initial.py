# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Configuration'
        db.create_table('configstore_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('_data', self.gf('django.db.models.fields.TextField')(db_column='data')),
        ))
        db.send_create_signal('configstore', ['Configuration'])

        # Adding unique constraint on 'Configuration', fields ['key', 'site']
        db.create_unique('configstore_configuration', ['key', 'site_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Configuration', fields ['key', 'site']
        db.delete_unique('configstore_configuration', ['key', 'site_id'])

        # Deleting model 'Configuration'
        db.delete_table('configstore_configuration')


    models = {
        'configstore.configuration': {
            'Meta': {'unique_together': "[('key', 'site')]", 'object_name': 'Configuration'},
            '_data': ('django.db.models.fields.TextField', [], {'db_column': "'data'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['configstore']