from django.conf.urls import patterns, include, url

urlpatterns = patterns('public.views',
    
    url(r'^login/$','user_login_page'),
    url(r'^login/default/(?P<default_username>\w*)/$','user_login_page'),
    url(r'^login/check/$','user_check_login'),

    url(r'^register/$','user_register_page'),
    url(r'^register/check/$','user_check_register'),
    url(r'^register/default/(?P<default_username>\w*)/$','user_register_page'),

    url(r'^config/(?P<username>\w+)/personal_info/$','userinfo_config_page'),
    url(r'^config/(?P<username>\w+)/info/$','userext_config_page'),

    url(r'^logout/$','user_logout_page'),
)
