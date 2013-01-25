import hyperadmin
from hyperadmin.resources.models import ModelResource

from django import forms

from configstore.configs import SINGLE_CONFIGS, LIST_CONFIGS
from configstore.models import Configuration, ConfigurationList
from configstore.endpoints import CreateEndpoint


class ConfigurationResourceMixin(object):
    create_endpoint_class = CreateEndpoint
    
    def get_configuration_options(self):
        raise NotImplementedError
    
    def get_configuration_instance(self):
        if 'instance' in self.state:
            key = self.state['instance'].key
        else:
            key = self.state.params['key']
        return self.get_configuration_options()[key]
    
    def get_form_class(self):
        return self.get_configuration_instance().form
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(ConfigurationResourceMixin, self).get_form_kwargs(**kwargs)
        return self.get_configuration_instance().get_form_kwargs(**kwargs)
    
    #TODO special add endpoint and add links
    
    def requires_select_configuration(self):
        if 'key' in self.state.params:
            return False
        if 'instance' in self.state and self.state['instance'].pk:
            return False
        return True
    
    def get_select_configuration_form_class(self):
        configuration_choices = list()
        
        class SelectConfigurationForm(forms.Form):
            key = forms.ChoiceField(choices=configuration_choices)
            
            def __init__(self, **kwargs):
                self.instance = kwargs.pop('instance', None)
                super(SelectConfigurationForm, self).__init__(**kwargs)
        
        return SelectConfigurationForm

class ConfigurationResource(ConfigurationResourceMixin, ModelResource):
    def get_configuration_options(self):
        return SINGLE_CONFIGS

hyperadmin.site.register(Configuration, ConfigurationResource)

class ConfigurationListResource(ConfigurationResourceMixin, ModelResource):
    def get_configuration_options(self):
        return LIST_CONFIGS

hyperadmin.site.register(ConfigurationList, ConfigurationListResource)
