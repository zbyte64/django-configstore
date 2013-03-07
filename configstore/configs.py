import base64
import threading
from Crypto.Cipher import AES
from Crypto.Hash import MD5

from django.conf import settings
from django.contrib.sites.models import Site

from configstore.models import Configuration
from configstore.serializer import make_serializers


ENCODER, DECODER = make_serializers()

CONFIG_CACHE = dict()
CONFIGS = dict()


class ConfigurationInstance(object):
    def __init__(self, key, name, form):
        """
        key is used for get_config(key)
        name is the label to be shown in the admin
        form is the form used to configure
        """
        self.key = key
        self.name = name
        self.form = form

    def serialize(self, data):
        return ENCODER.encode(data)
    
    def deserialize(self, datum):
        return DECODER.decode(datum)

    def get_data(self):
        """
        Returns a dictionary like object representing the stored configuration
        """
        #CONSIDER should we plug in caching here?
        try:
            configuration = Configuration.objects.get(key=self.key, site=Site.objects.get_current())
        except Configuration.DoesNotExist:
            return {}
        else:
            return self.deserialize(configuration.data)

    def set_data(self, data, commit=True, site=None):
        if site is None:
            site = Site.objects.get_current()
        #TODO use get_or_create instead of create, look at return types and stuff
        try:
            configuration = Configuration.objects.get(key=self.key, site=site)
        except Configuration.DoesNotExist:
            configuration = Configuration()
            configuration.key = self.key
            configuration.site = Site.objects.get_current()
        configuration.data = self.serialize(data)
        if commit:
            configuration.save()
        return configuration

    def get_form_builder(self):
        """
        Returns a function that is responsible for building a form
        """
        #CONSIDER we don't simply return a form because of the admin
        def form_builder(*args, **kwargs):
            kwargs['key'] = self.key
            kwargs['configuration'] = self
            return self.form(*args, **kwargs)
        return form_builder


class AESEncryptedConfiguration(ConfigurationInstance):
    def deserialize(self, datum):
        data = self.decrypt_data(datum, str(settings.SITE_ID))
        return DECODER.decode(data)

    def serialize(self, data):
        data = ENCODER.encode(data)
        return self.encrypt_data(self.pad_string(data, AES.block_size), str(settings.SITE_ID))

    def encrypt_data(self, value, iv):
        iv = MD5.new("%s!%s" % (iv, settings.SECRET_KEY)).digest()
        enc = AES.new(settings.SECRET_KEY[:32], AES.MODE_CBC, iv)  # Guess why :32?
        value = enc.encrypt(self.pad_string(value, AES.block_size))
        return base64.b64encode(value)

    def decrypt_data(self, value, iv):
        value = base64.b64decode(value)
        iv = MD5.new("%s!%s" % (iv, settings.SECRET_KEY)).digest()
        dec = AES.new(settings.SECRET_KEY[:32], AES.MODE_CBC, iv)
        return dec.decrypt(value).strip()

    def pad_string(self, string, block_size):
        str_size = len(string)
        missing = block_size - (str_size % block_size)
        return str(string) + missing * b" "


def _wrap(func_name):
    #TODO perserve docs and function name
    def wrapper(self, *args, **kwargs):
        self._load()
        return getattr(self.data.config, func_name)(*args, **kwargs)
    return wrapper

class LazyDictionary(object): #this is one ugly class
    def __init__(self, loader):
        '''
        loader is a callable that returns a dictionary
        '''
        self.loader = loader
        self.data = threading.local()

    # TODO: Since Django likes to lazy we should consider looking if they have
    # already done something like this.
    __contains__ = _wrap('__contains__')
    __format__ = _wrap('__format__')
    __getitem__ = _wrap('__getitem__')
    __iter__ = _wrap('__iter__')
    __len__ = _wrap('__len__')
    __setitem__ = _wrap('__setitem__')
    __str__ = _wrap('__str__')
    copy = _wrap('copy')
    get = _wrap('get')
    has_key = _wrap('has_key')
    items = _wrap('items')
    iteritems = _wrap('iteritems')
    iterkeys = _wrap('iterkeys')
    itervalues = _wrap('itervalues')
    keys = _wrap('keys')
    pop = _wrap('pop')
    popitem = _wrap('popitem')
    setdefault = _wrap('setdefault')
    update = _wrap('update')
    values = _wrap('values')

    def _load(self):
        if not hasattr(self.data, 'config'):
            self.data.config = self.loader()
    
    def _reset(self):
        if hasattr(self.data, 'config'):
            del self.data.config

def register(configuration_instance):
    CONFIGS[configuration_instance.key] = configuration_instance

def get_config(key):
    """
    Returns a lazy object that will be evaluated at the time of getting the first attribute
    The lazy object will be unique to each thread so values may be changed on the fly
    The object also gets purged upon the beginning of each request
    """
    if key not in CONFIG_CACHE:
        CONFIG_CACHE[key] = LazyDictionary(CONFIGS[key].get_data)
    return CONFIG_CACHE[key]

