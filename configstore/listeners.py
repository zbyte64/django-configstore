from configstore.configs import CONFIG_CACHE, SINGLE_CONFIGS, LIST_CONFIGS
from django.core.signals import request_started


def nuke_cache(**kwargs):
    keys = SINGLE_CONFIGS.keys() + LIST_CONFIGS.keys()
    for key in keys:
        if key in CONFIG_CACHE:
            #the following is necessary because not everyone will keep calling get_config
            config = CONFIG_CACHE[key]
            config._reset()

request_started.connect(nuke_cache)
