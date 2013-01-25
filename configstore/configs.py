from django.contrib.sites.models import Site

from configstore.models import Configuration, ConfigurationList

import threading

CONFIG_CACHE = dict()
SINGLE_CONFIGS = dict()
LIST_CONFIGS = dict()

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
        raise NotImplementedError
    
    def register_instance(self):
        raise NotImplementedError
    
    def get_form_kwargs(self, **kwargs):
        kwargs.setdefault('key', self.key)
        return kwargs
    
    def get_form_builder(self):
        """
        Returns a function that is responsible for building a form
        """
        #CONSIDER we don't simply return a form because of the admin
        def form_builder(*args, **kwargs):
            kwargs = self.get_form_kwargs(**kwargs)
            return self.form(*args, **kwargs)
        return form_builder

class ConfigurationSingleton(ConfigurationInstance):
    def get_config(self):
        """
        Returns a dictionary like object representing the stored configuration
        """
        try:
            configuration = Configuration.objects.get(key=self.key, site=Site.objects.get_current())
        except Configuration.DoesNotExist:
            return {}
        else:
            return configuration.data
    
    def get_config_object(self):
        return LazyDictionary(self.get_config)
    
    def register_instance(self):
        SINGLE_CONFIGS[self.key] = self

class ConfigurationList(ConfigurationInstance):
    def __init__(self, group, **kwargs):
        self.group = group
        super(ConfigurationList, self).__init__(**kwargs)
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(ConfigurationList, self).get_form_kwargs(**kwargs)
        kwargs.setdefault('group', self.group)
        return kwargs
    
    def get_config(self):
        """
        Returns a list of dictionary like object representing the stored configuration
        """
        configurations = ConfigurationList.objects.filter(group=self.group, site=Site.objects.get_current())
        return [configuration.data for configuration in configurations]
    
    def get_config_object(self):
        return LazyList(self.get_config)
    
    def register_instance(self):
        LIST_CONFIGS[self.key] = self

def _wrap(func_name):
    #TODO perserve docs and function name
    def wrapper(self, *args, **kwargs):
        self._load()
        return getattr(self.data.config, func_name)(*args, **kwargs)
    return wrapper

class LazyMixin(object):
    def __init__(self, loader):
        '''
        loader is a callable that returns a dictionary
        '''
        self.loader = loader
        self.data = threading.local()
    
    def _load(self):
        if not hasattr(self.data, 'config'):
            self.data.config = self.loader()
    
    def _reset(self):
        if hasattr(self.data, 'config'):
            del self.data.config

class LazyDictionary(LazyMixin): #this is one ugly class
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

class LazyList(LazyMixin):
    __contains__ = _wrap('__contains__')
    __getitem__ = _wrap('__getitem__')
    __iter__ = _wrap('__iter__')
    __len__ = _wrap('__len__')
    __setitem__ = _wrap('__setitem__')
    __str__ = _wrap('__str__')
    count = _wrap('count')
    index = _wrap('index')
    sort = _wrap('sort')
    reverse = _wrap('reverse')

def register(klass, key, **params):
    params['key'] = key
    instance = klass(**params)
    instance.register_instance()
    return instance

def get_config(key):
    '''
    Returns a lazy object that will be evaluated at the time of getting the first attribute
    The lazy object will be unique to each thread so values may be changed on the fly
    The object also gets purged upon the begining of each request
    '''
    if key not in CONFIG_CACHE:
        if key in SINGLE_CONFIGS:
            datum = SINGLE_CONFIGS[key].get_config_object()
        else:
            datum = LIST_CONFIGS[key].get_config_object()
        CONFIG_CACHE[key] = datum
    return CONFIG_CACHE[key]

