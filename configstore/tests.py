import unittest

from django.test import TestCase
from django.test.client import Client
from django.core import urlresolvers
from django.contrib import admin
from django import forms

from configs import ConfigurationInstance, register, get_config, CONFIG_CACHE
from forms import ConfigurationForm

class TestConfigurationForm(ConfigurationForm):
    setting1 = forms.CharField()
    setting2 = forms.IntegerField()

class ConfigStoreTest(TestCase):
    def setUp(self):
        if hasattr(CONFIG_CACHE, 'test'):
            delattr(CONFIG_CACHE, 'test')

    def test_register_and_retrieve_config(self):
        instance = ConfigurationInstance('test', 'test', TestConfigurationForm)
        register(instance)
        form_builder = instance.get_form_builder()
        lazydictionary_post = get_config('test')
        form = form_builder({'setting1':'wooot', 'setting2':'2', 'site':'1'}, {})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertNotEqual(0, len(get_config('test').items()))
        self.assertNotEqual(0, len(lazydictionary_post.items()))
    
    def test_empty_config(self):
        instance = ConfigurationInstance('test', 'test', TestConfigurationForm)
        register(instance)
        lazydictionary_pre = get_config('test')
        self.assertEqual(0, len(lazydictionary_pre.items()))
