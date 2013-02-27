from django.db import models
from django.contrib.sites.models import Site
from serializer import make_serializers
from Crypto.Cipher import AES
import base64
from django.conf import settings

ENCODER, DECODER = make_serializers()


class Configuration(models.Model):
    key = models.CharField(max_length=50)
    site = models.ForeignKey(Site)
    _data = models.TextField(db_column='data')
    is_crypto = models.BooleanField(default=False)

    def get_data(self):
        if self._data:
            if self.is_crypto:
                data = self.decrypt_data(self._data)
                return DECODER.decode(data)
            else:
                return DECODER.decode(self._data)
        return {}

    def set_data(self, data):
        if self.is_crypto:
            data = ENCODER.encode(data)
            self._data = self.encrypt_data(data)
        else:
            self._data = ENCODER.encode(data)

    data = property(get_data, set_data)

    def encrypt_data(self, value):
        enc = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)  # Guess why :32?
        value = enc.encrypt(self.pad_string(value, AES.block_size))
        return base64.b64encode(value)

    def decrypt_data(self, value):
        value = base64.b64decode(value)
        dec = AES.new(settings.SECRET_KEY[:32], AES.MODE_ECB)
        return dec.decrypt(value).strip()

    def set_key_value(self, key, value):
        r = self.get_data()
        r[key] = value
        return self.set_data(r)

    def pad_string(self, string, block_size):
        str_size = len(string)
        missing = block_size - (str_size % block_size)
        return str(string) + missing * u" "

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