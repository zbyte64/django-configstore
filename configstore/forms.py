from django import forms
from django.utils import simplejson
from django.contrib.sites.models import Site
from django.core.serializers.json import DjangoJSONEncoder

from models import Configuration

class ConfigurationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.key = kwargs.pop('key')
        super(ConfigurationForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.initial.update(self.instance.data)

    def save(self, commit=True):
        instance = super(ConfigurationForm, self).save(False)
        data = dict(self.cleaned_data)
        del data['site']
        instance.data = data
        instance.key = self.key
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Configuration
        fields = ['site']


