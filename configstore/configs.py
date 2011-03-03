from django.contrib.sites.models import Site

from models import Configuration

import threading

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

    def get_config(self):
        """
        Returns a dictionary like object representing the stored configuration
        """
        #CONSIDER should we plug in caching here?
        try:
            configuration = Configuration.objects.get(key=self.key, site=Site.objects.get_current())
        except Configuration.DoesNotExist:
            return {}
        else:
            return configuration.data

    def get_form_builder(self):
        """
        Returns a function that is responsible for building a form
        """
        #CONSIDER we don't simply return a form because of the admin
        def form_builder(*args, **kwargs):
            kwargs['key'] = self.key
            return self.form(*args, **kwargs)
        return form_builder

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
    '''
    Returns a lazy object that will be evaluated at the time of getting the first attribute
    The lazy object will be unique to each thread so values may be changed on the fly
    The object also gets purged upon the begining of each request
    '''
    if key not in CONFIG_CACHE:
        CONFIG_CACHE[key] = LazyDictionary(CONFIGS[key].get_config)
    return CONFIG_CACHE[key]

