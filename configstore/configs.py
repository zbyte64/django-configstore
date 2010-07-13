from django.contrib.sites.models import Site

from models import Configuration

import threading

CONFIG_CACHE = threading.local()
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

def _wrap(func_name):
    def wrapper(self, *args, **kwargs):
        self._load()
        return getattr(super(LazyDictionary, self), func_name)(*args, **kwargs)
    return wrapper

class LazyDictionary(dict): #this is one ugly class
    def __init__(self, loader):
        '''
        loader is a callable that returns a dictionary
        '''
        self.loader = loader
        self.loaded = False
    
    items = _wrap('items')
    keys = _wrap('keys')
    values = _wrap('values')
    setdefault = _wrap('setdefault')
    update = _wrap('update')
    pop = _wrap('pop')
    popitem = _wrap('popitem')
    get = _wrap('get')
    copy = _wrap('copy')
    __iter__ = _wrap('__iter__')
    __getitem__ = _wrap('__getitem__')
    __setitem__ = _wrap('__setitem__')
    __contains__ = _wrap('__contains__')
    __format__ = _wrap('__format__')
    __str__ = _wrap('__str__')

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

