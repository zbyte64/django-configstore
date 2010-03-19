from django.contrib.sites.models import Site

from models import Configuration

import threading

CONFIG_CACHE = threading.local() #TODO: not lazy enough, threads get recycled in django!
CONFIGS = dict()

class ConfigurationInstance(object):
    def __init__(self, key, name, form):
        self.key = key
        self.name = name
        self.form = form

    def get_config(self):
        try:
            configuration = Configuration.objects.get(key=self.key, site=Site.objects.get_current())
        except Configuration.DoesNotExist:
            return {}
        else:
            return configuration.data

    def get_form_builder(self):
        def form_builder(*args, **kwargs):
            kwargs['key'] = self.key
            return self.form(*args, **kwargs)
        return form_builder

class LazyDictionary(dict): #this is one ugly class
    def __init__(self, loader):
        '''
        loader is a callable that returns a dictionary
        '''
        self.loader = loader
        self.loaded = False

    def items(self):
        self._load()
        return super(LazyDictionary, self).items()

    def __iter__(self):
        self._load()
        return super(LazyDictionary, self).__iter__()
    
    def __getitem__(self, key):
        self._load()
        return super(LazyDictionary, self).__getitem__(key)

    def __contains__(self, key):
        self._load()
        return super(LazyDictionary, self).__contains__(key)

    def get(self, *args, **kwargs):
        self._load()
        return super(LazyDictionary, self).get(*args, **kwargs)

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
        setattr(CONFIG_CACHE, key, LazyDictionary(CONFIGS[key].get_config))
    return getattr(CONFIG_CACHE, key)

