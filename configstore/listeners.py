from configs import CONFIG_CACHE, CONFIGS
from django.core.signals import request_started

def nuke_cache(**kwargs):
    for key in CONFIGS.keys():
        if hasattr(CONFIG_CACHE, key):
            #the following is necessary because not everyone will keep calling get_config
            config = getattr(CONFIG_CACHE, key)
            config.clear()
            config.loaded = False
            #this might be redundant
            delattr(CONFIG_CACHE, key)
    
request_started.connect(nuke_cache)
