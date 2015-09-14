from django.conf.urls import patterns, include, url
import settings

urlpatterns = patterns('forum.views',
    url(r'^board/$','forum_board_page'),
    url(r'^board/(?P<bid>\d+)/$','forum_thread_page'),
    url(r'^board/goto/$','set_thread_per_page'),
    url(r'^board/thread/goto/$','set_post_per_page'),
    url(r'^board/(?P<bid>\d+)-(?P<page>\d+)/$','forum_thread_page'),    
    url(r'^board/(?P<bid>\d+)-(?P<page>\d+)-(?P<thread_per_page>\d+)/$','forum_thread_page'),
    url(r'^board/thread/(?P<tid>\d+)/$','forum_post_page'),
    url(r'^board/thread/(?P<tid>\d+)-(?P<page>\d+)/$','forum_post_page'),
    url(r'^board/thread/(?P<tid>\d+)-(?P<page>\d+)-(?P<post_per_page>\d+)/$','forum_post_page'),
    #url(r'^board/(?P<bid>)\d+/$',''),
    url(r'^admin/sync_board/$','sync_all_board'),
    url(r'^profile/image$','forum_uploadimage_page'),
    url(r'^profile/password$','forum_password_page'),
    url(r'^profile/basic$','forum_basicprofile_page'),
    url(r'^profile/$','forum_profile_page'),
)
