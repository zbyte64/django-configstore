from django.db import models
from django.contrib.sites.models import Site

class Configuration(models.Model):
    key = models.CharField(max_length=50)
    site = models.ForeignKey(Site)
    _data = models.TextField(db_column='data')
    is_crypto = models.BooleanField(default=False)

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    data = property(get_data, set_data)

    def set_key_value(self, key, value):
        r = self.get_data()
        r[key] = value
        return self.set_data(r)

    @property
    def name(self):
        from configs import CONFIGS
        try:
            return CONFIGS[self.key].name
        except KeyError:
            return self.key

    def __unicode__(self):
        return '%s: %s' % (self.key, self.site)

    class Meta:
        unique_together = [('key', 'site')]