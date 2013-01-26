from django.db import models
from django.contrib.sites.models import Site

from configstore.serializer import make_serializers


ENCODER, DECODER = make_serializers()

class ConfigurationMixin(models.Model):
    key = models.CharField(max_length=50)
    site = models.ForeignKey(Site)
    _data = models.TextField(db_column='data')
    
    def get_data(self):
        if self._data:
            return DECODER.decode(self._data)
        return {}
    
    def set_data(self, data):
        self._data = ENCODER.encode(data)
        
    data = property(get_data, set_data)
    
    def __unicode__(self):
        return u'%s: %s' % (self.name, self.site)
    
    class Meta:
        abstract = True

class Configuration(ConfigurationMixin):
    @property
    def name(self):
        from configstore.configs import SINGLE_CONFIGS
        try:
            return SINGLE_CONFIGS[self.key].name
        except KeyError:
            return self.key
    
    class Meta:
        unique_together = [('key', 'site')]

class ConfigurationList(ConfigurationMixin):
    label = models.CharField(max_length=50)
    group = models.CharField(max_length=50) #key represents the instance used
    
    @property
    def name(self):
        from configstore.configs import LIST_CONFIGS
        try:
            return LIST_CONFIGS[self.key].name
        except KeyError:
            return self.key
    
    #TODO only in django 1.5
    #class Meta:
    #    index_together = [('group', 'site')]
