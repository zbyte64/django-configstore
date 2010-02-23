from django.db import models
from django.contrib.sites.models import Site
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder

class Configuration(models.Model):
    key = models.CharField(max_length=50)
    site = models.ForeignKey(Site)
    _data = models.TextField(db_column='data')
    
    def get_data(self):
        if self._data:
            return simplejson.loads(self._data)
        return {}
    
    def set_data(self, data):
        self._data = simplejson.dumps(data, cls=DjangoJSONEncoder)
        
    data = property(get_data, set_data)

    def __unicode__(self):
        return '%s: %s' % (self.key, self.site)

    class Meta:
        unique_together = [('key', 'site')]
