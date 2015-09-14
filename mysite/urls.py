from django.conf.urls import patterns, include, url
import settings

from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()  # dajaxice
# dajaxice 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import public
urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^public/',include('public.urls')),
    url(r'^forum/',include('forum.urls')),
    # dajaxice
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^image_upload/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)

urlpatterns += staticfiles_urlpatterns()
