"""
Contains custom json encoders and decoders for handling more complex data types
"""
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.db import models
from django.utils import simplejson

from decimal import Decimal

class Handler(object):
    def encode(self, obj):
        '''
        Return a dictionary with our own __type__
        '''
        raise NotImplementedError
    
    def decode(self, dct):
        '''
        Return an object from a dictionary
        '''
        raise NotImplementedError

class ModelHandler(Handler):
    key = 'ModelReference'
    instancetype = models.Model
    
    def __init__(self, nullify_notfound=False):
        self.nullify_notfound = nullify_notfound

    def encode(self, obj):
        return {'__type__':self.key,
                'app':obj._meta.app_label,
                'model':obj._meta.object_name.lower(),
                'pk':obj.pk}
    
    def decode(self, dct):
        del dct['__type__']
        ct = ContentType.objects.get(app_label=dct.pop('app'), 
                                         model=dct.pop('model'))
        try:
            kwargs = dict([(str(key), value) for key, value in dct.iteritems()])
            return ct.get_object_for_this_type(**kwargs)
        except ObjectDoesNotExist:
            if not self.nullify_notfound:
                raise
            return None

class DecimalHandler(Handler):
    key = 'Decimal'
    instancetype = Decimal
    
    def encode(self, obj):
        return {'__type__':self.key,
                'value':str(obj)}
    
    def decode(self, dct):
        return Decimal(dct['value'])

class JSONDecoder(simplejson.JSONDecoder):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('object_hook', self.decode_objects)
        self.handlers = kwargs.pop('handlers')
        self.handlers_by_key = dict([(handler.key, handler) for handler in self.handlers])
        super(JSONDecoder, self).__init__(*args, **kwargs)

    def decode_objects(self, dct):
        if '__type__' in dct:
            return self.handlers_by_key[dct['__type__']].decode(dct)
        return dct

class JSONEncoder(DjangoJSONEncoder):
    def __init__(self, *args, **kwargs):
        self.handlers = kwargs.pop('handlers')
        super(JSONEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, (QuerySet, list)):
            return map(self.default, obj)
        for handler in self.handlers:
            if isinstance(obj, handler.instancetype):
                return handler.encode(obj)
        return super(JSONEncoder, self).default(obj)

def make_serializers():
    handlers = [ModelHandler(), DecimalHandler()]
    #CONSIDER it might be a good idea to allow registering more serializers
    return JSONEncoder(handlers=handlers), JSONDecoder(handlers=handlers)

