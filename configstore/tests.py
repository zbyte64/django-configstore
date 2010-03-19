import unittest

from django.test import TestCase
from django.test.client import Client
from django.core import urlresolvers
from django.contrib import admin
from django.contrib.auth.models import User
from django import forms

from configs import ConfigurationInstance, register, get_config, CONFIG_CACHE, CONFIGS
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
        self.assertNotEqual(0, len(get_config('test').items()))
        self.assertNotEqual(0, len(lazydictionary_post.items()))
    
    def test_empty_config(self):
        lazydictionary_pre = get_config('test')
        self.assertEqual(0, len(lazydictionary_pre.items()))
    
    def test_configstore_admin(self):
        admin.autodiscover()
        admin_entry = admin.site._registry[Configuration]
        class dummy_user(object):
            has_perm = lambda *x: False
            get_and_delete_messages = lambda *x: []
            
        class dummy_request(object):
            REQUEST = dict()
            POST = dict()
            GET = dict()
            FILES = dict()
            user = dummy_user()
        admin_entry.add_view(dummy_request())
        #key=test
    
    def test_complex_config(self):
        form_builder = self.complex_instance.get_form_builder()
        lazydictionary_post = get_config('testcomplex')
        test_user = User.objects.get_or_create(username='testuser')[0]
        form = form_builder({'amount':'5.00', 'user':test_user.pk, 'site':'1'}, {})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertNotEqual(0, len(get_config('testcomplex').items()))
        self.assertNotEqual(0, len(lazydictionary_post.items()))
        config = get_config('testcomplex')
        self.assertTrue(isinstance(config['amount'], Decimal))
        self.assertEqual(Decimal('5.00'), config['amount'])
        self.assertTrue(isinstance(config['user'], User))
        self.assertEqual(test_user.pk, config['user'].pk)
    
    def test_nuke_cache(self):
        get_config('test').items()
        nuke_cache()
        for key in CONFIGS.keys():
            self.assertFalse(hasattr(CONFIG_CACHE, key))
        
