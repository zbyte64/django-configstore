from django.test import TestCase
from django.core import urlresolvers
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django import forms
from django.template import Template, Context

from configs import ConfigurationInstance, register, get_config, CONFIG_CACHE
from forms import ConfigurationForm
from models import Configuration
from listeners import nuke_cache

from decimal import Decimal

class TestConfigurationForm(ConfigurationForm):
    setting1 = forms.CharField()
    setting2 = forms.IntegerField()

class TestComplexConfigurationForm(ConfigurationForm):
    amount = forms.DecimalField()
    user = forms.ModelChoiceField(queryset=User.objects.all())

class ConfigStoreTest(TestCase):
    # CONSIDER: There are no views to test do we need this?
    # urls = 'configstore.test_urls'

    def setUp(self):
        if hasattr(CONFIG_CACHE, 'test'):
            delattr(CONFIG_CACHE, 'test')
        if hasattr(CONFIG_CACHE, 'testcomplex'):
            delattr(CONFIG_CACHE, 'testcomplex')
        self.instance = ConfigurationInstance('test', 'test', TestConfigurationForm)
        register(self.instance)
        self.complex_instance = ConfigurationInstance('testcomplex', 'testcomplex', TestComplexConfigurationForm)
        register(self.complex_instance)

    def test_register_and_retrieve_config(self):
        form_builder = self.instance.get_form_builder()
        lazydictionary_post = get_config('test')
        form = form_builder({'setting1':'wooot', 'setting2':'2', 'site':'1'}, {})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        lazydictionary_post._reset()
        self.assertNotEqual(0, len(lazydictionary_post.items()))
        self.assertNotEqual(0, len(lazydictionary_post.items()))

    def test_empty_config(self):
        lazydictionary_pre = get_config('test')
        self.assertEqual(0, len(lazydictionary_pre.items()))

    def login(self):
        admin_user = User(username='configadmin', is_staff=True, is_superuser=True)
        admin_user.set_password('configadmin')
        admin_user.save()
        assert self.client.login(username=admin_user.username, password='configadmin')

    def test_configstore_admin(self):
        self.login()
        self.client.get(urlresolvers.reverse('admin:configstore_configuration_add'))
        self.client.get(urlresolvers.reverse('admin:configstore_configuration_add'), data={'key':'test'})
        self.client.get(urlresolvers.reverse('admin:configstore_configuration_changelist'))

    def test_congistore_admin_handles_unknown_keys(self):
        Configuration(key='unknown-key', site=Site.objects.get_current()).save()
        self.login()
        self.client.get(urlresolvers.reverse('admin:configstore_configuration_changelist'))

    def test_complex_config(self):
        form_builder = self.complex_instance.get_form_builder()
        lazydictionary_post = get_config('testcomplex')
        test_user = User.objects.get_or_create(username='testuser')[0]
        form = form_builder({'amount':'5.00', 'user':test_user.pk, 'site':'1'}, {})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertNotEqual(0, len(get_config('testcomplex').items()))
        self.assertNotEqual(0, len(lazydictionary_post.items()))
        nuke_cache()
        config = get_config('testcomplex')
        self.assertTrue(isinstance(config['amount'], Decimal))
        self.assertEqual(Decimal('5.00'), config['amount'])
        self.assertTrue(isinstance(config['user'], User))
        self.assertEqual(test_user.pk, config['user'].pk)

    def test_nuke_cache(self):
        my_config = get_config('test')
        my_config._load()
        nuke_cache()
        self.assertFalse(hasattr(my_config.data, 'config'))
        my_config._load()
        self.assertTrue(hasattr(my_config.data, 'config'))

    def test_with_config_templatetag(self):
        self.test_register_and_retrieve_config()
        template_string = """
        {% load configuration %}
        {% withconfig "test" as testconfig %}
            {{testconfig.setting1}}
        {% endwithconfig %}
        """
        template = Template(template_string)
        result = template.render(Context({}))
        self.assertTrue('wooot' in result)
