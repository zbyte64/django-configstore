from django.contrib.sites.models import Site

from models import Configuration

import threading

CONFIG_CACHE = threading.local()
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
        return getattr(super(LazyDictionary, self), func_name)(*args, **kwargs)
    return wrapper

class LazyDictionary(dict): #this is one ugly class
    def __init__(self, loader):
        '''
        loader is a callable that returns a dictionary
        '''
        self.loader = loader
        self.loaded = False

    # TODO: Since Django likes to lazy we should consider looking if they have
    # already done something like this.
    __contains__ = _wrap('__contains__')
    __format__ = _wrap('__format__')
    __getitem__ = _wrap('__getitem__')
    __iter__ = _wrap('__iter__')
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
        if not self.loaded:
            self.loaded = True
            self.update(self.loader())

def register(configuration_instance):
    CONFIGS[configuration_instance.key] = configuration_instance

def get_config(key):
    '''
    Returns a lazy object that will be evaluated at the time of getting the first attribute
    The lazy object will be unique to each thread so values may be changed on the fly
    The object also gets purged upon the begining of each request
    '''
    if not hasattr(CONFIG_CACHE, key):
        setattr(CONFIG_CACHE, key, LazyDictionary(CONFIGS[key].get_config))
    return getattr(CONFIG_CACHE, key)

