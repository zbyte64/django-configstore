from django.http import HttpResponse

from configstore.configs import get_config

my_config = get_config('example')

def display_my_config(request):
    return HttpResponse(unicode(my_config), content_type='text/plain')
