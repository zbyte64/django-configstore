from configs import CONFIG_CACHE, CONFIGS
from django.core.signals import request_started

def nuke_cache(**kwargs):
    for key in CONFIGS.keys():
        if key in CONFIG_CACHE:
            #the following is necessary because not everyone will keep calling get_config
            config = CONFIG_CACHE[key]
            config._reset()

request_started.connect(nuke_cache)
