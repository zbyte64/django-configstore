from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'example_app.views.display_my_config'),
    (r'^admin/', include(admin.site.urls)),
)
