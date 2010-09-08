from django.http import HttpResponse

from configstore.configs import get_config

def display_my_config(request):
    config = get_config('example')
    return HttpResponse(unicode(config), content_type='text/plain')
