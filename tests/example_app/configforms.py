from django import forms
from django.contrib.auth.models import User

from configstore.configs import ConfigurationInstance, register
from configstore.forms import ConfigurationForm

class ExampleConfigurationForm(ConfigurationForm):
    amount = forms.DecimalField()
    message = forms.CharField()
    user = forms.ModelChoiceField(queryset=User.objects.all())

complex_instance = ConfigurationInstance('example', 'Example Config', ExampleConfigurationForm)
register(complex_instance)
