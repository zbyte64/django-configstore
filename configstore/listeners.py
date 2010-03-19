from configs import CONFIG_CACHE, CONFIGS
from django.core.signals import request_started

def nuke_cache(**kwargs):
    for key in CONFIGS.keys():
        if hasattr(CONFIG_CACHE, key):
            delattr(CONFIG_CACHE, key)
    
request_started.connect(nuke_cache)
