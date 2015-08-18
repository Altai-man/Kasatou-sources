from django.conf.urls import patterns, include, url
from Layers import views
from django.contrib import admin
from Kasatou import settings
admin.autodiscover()
from .user_urls import user_patterns
from .post_urls import post_patterns

urlpatterns = patterns(
    '',

    # Index
    url(r'^$', views.IndexView.as_view(), name='index'),

    # Board
    url(r'^(?P<board_name>[a-z]{1,3})/(?P<page>[1-9]?)$', views.BoardView.as_view(), name='board_view'),

    # Thread
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<pk>[0-9]+)/$', views.ThreadView.as_view(), name='thread_view'),

    # Update thread
    url(r'^(?P<board_name>[a-z]{1,3})/thread/update/(?P<thread_id>[0-9]+)/(?P<posts_numb>[0-9]+)$',
        views.ThreadUpdateView.as_view(), name='thread_update'),

    # User stuff.
    url(r'', include(post_patterns)),

    # User stuff.
    url(r'', include(user_patterns)),

    # Search
    url(r'^search/$', views.SearchView.as_view(), name='search'),

    # Add thread
    url(r'^thread_add/$', views.ThreadCreating.as_view(), name='thread_add'),

    # Get single thread
    url(r'^thread/get/(?P<pk>[0-9]+)/$', views.SingleThreadView.as_view(), name='thread_get'),

    # Error page.
    url(r'^closed/$', views.closed, name='closed'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns(
    '',

    (r'^media\/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),

    (r'^static\/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
)
