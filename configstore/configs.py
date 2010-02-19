from django.contrib.sites.models import Site

from models import Configuration

import threading

CONFIG_CACHE = threading.local()
CONFIGS = dict()

class ConfigurationInstance(object):
    form = None
    key = None
    name = None

    def get_config(self):
        try:
            configuration = Configuration.objects.get(key=self.key, site=Site.objects.get_current())
        except Configuration.DoesNotExist:
            return {}
        else:
            return configuration.data

    def get_form_builder(self):
        return lambda data, files, **kwargs: self.form(data, files, key=self.key, **kwargs)

class LazyDictionary(dict):
    def __init__(self, loader):
        '''
        loader is a callable that returns a dictionary
        '''
        self.loader = loader
        self.loaded = False

    def __getitem__(self, key):
        self._load()        
        return super(LazyDictionary, self).__getitem__(key)

    def __contains__(self, key):
        self._load()
        return super(LazyDictionary, self).__contains__(key)

    def _load(self):
        if not self.loaded:
            self.loaded = True
            self.update(self.loader())

def register(configuration_instance):
    CONFIGS[configuration_instance.key] = configuration_instance

def get_config(key):
    '''
    Returns a lazy object that will be evaluated at the time of getting the first attribute
    The lazy object will be unique to each thread so values may be changed on the fly
    '''
    if not hasattr(CONFIG_CACHE, key):
        setattr(CONFIG_CACHE, key, LazyDictionary(CONFIGS[key].get_config()))
    return getattr(CONFIG_CACHE, key)

