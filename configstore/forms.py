from django import forms
from django.contrib.sites.models import Site

class ConfigurationForm(forms.Form):
    site = forms.ModelChoiceField(Site.objects.all())
    
    def __init__(self, *args, **kwargs):
        self.key = kwargs.pop('key')
        self.configuration = kwargs.pop('configuration')
        self.instance = kwargs.pop('instance', None)
        super(ConfigurationForm, self).__init__(*args, **kwargs)
        self.instance = self.configuration.get_data()
        if self.instance:
            initial = self.instance
            # model based fields don't know what to due with objects,
            # but they do know what to do with pks
            for key, value in initial.items():
                if hasattr(value, 'pk'):
                    initial[key] = value.pk
            self.initial.update(initial)

    def save(self, commit=True):
        data = dict(self.cleaned_data)
        site = data.pop('site')
        return self.configuration.set_data(data, commit=commit, site=site)

    def save_m2m(self):
        return True

    def config_task(self):
        return "No configuration action defined for %s" % self.key

