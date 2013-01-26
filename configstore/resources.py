import hyperadmin
from hyperadmin.resources.models import ModelResource

from django import forms

from configstore.configs import SINGLE_CONFIGS, LIST_CONFIGS
from configstore.models import Configuration, ConfigurationList
from configstore.endpoints import CreateEndpoint


class ConfigurationResourceMixin(object):
    list_display = ['name', 'key', 'site']
    list_filter = ['site']
    
    create_endpoint_class = CreateEndpoint
    
    def get_configuration_options(self):
        raise NotImplementedError
    
    def get_configuration_instance(self):
        if 'item' in self.state:
            key = self.state['item'].instance.key
        else:
            key = self.state.params['key']
        return self.get_configuration_options()[key]
    
    def get_form_class(self):
        if self.requires_select_configuration():
            return self.get_select_configuration_form_class()
        return self.get_configuration_instance().form
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(ConfigurationResourceMixin, self).get_form_kwargs(**kwargs)
        if not self.requires_select_configuration():
            return self.get_configuration_instance().get_form_kwargs(**kwargs)
        return kwargs
    
    def requires_select_configuration(self):
        if 'key' in self.state.params:
            return False
        if 'item' in self.state and self.state['item'].instance.pk:
            return False
        return True
    
    def get_select_configuration_form_class(self):
        configuration_choices = [(key, instance.name) for key, instance in self.get_configuration_options().iteritems()]
        
        class SelectConfigurationForm(forms.Form):
            key = forms.ChoiceField(choices=configuration_choices)
            
            def __init__(self, **kwargs):
                self.instance = kwargs.pop('instance', None)
                super(SelectConfigurationForm, self).__init__(**kwargs)
            
            def save(self, **kwargs):
                return None
        
        return SelectConfigurationForm

class ConfigurationResource(ConfigurationResourceMixin, ModelResource):
    def get_configuration_options(self):
        return SINGLE_CONFIGS

hyperadmin.site.register(Configuration, ConfigurationResource)

class ConfigurationListResource(ConfigurationResourceMixin, ModelResource):
    list_display = ['label', 'name', 'key', 'site']
    
    def get_configuration_options(self):
        return LIST_CONFIGS

hyperadmin.site.register(ConfigurationList, ConfigurationListResource)
