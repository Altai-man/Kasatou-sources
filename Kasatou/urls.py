from django.conf.urls import patterns, include, url
from Layers import views
from django.contrib import admin
from Kasatou import settings
admin.autodiscover()

urlpatterns = patterns(
    '',

    # Admin
    url(r'^bunny/', include(admin.site.urls)),

    # Index
    url(r'^$', views.IndexView.as_view(), name='index'),

    # Board
    url(r'^(?P<board_name>[a-z]{1,3})/(?P<page>[1-9]?)$', views.BoardView.as_view(), name='board_view'),

    # Thread
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<pk>[0-9]+)/$', views.ThreadView.as_view(), name='thread_view'),

    # Search
    url(r'^search/$', views.SearchView.as_view(), name='search'),

    # Add thread
    url(r'^thread_add/$', views.ThreadCreating.as_view(), name='thread_add'),

    # Add post
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<thread_id>[0-9]+)/add_post/$', views.post_adding, name='post_add'),

    # Remove post
    url(r'post_deleting/(?P<p_id>[0-9]+)', views.post_deleting, name='post_deleting'),

    # Edit post
    url(r'post_editing/(?P<p_id>[0-9]+)', views.PostEditing.as_view()),

    # Urls for auth pages
    url(r'^register/(?P<code>.*)/$', views.Register.as_view(), name='register_get'),

    url(r'^register/$', views.Register.as_view(), name='register_accept'),

    url(r'^login/$', views.Login.as_view(), name='login'),

    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^profile/$', views.Profile.as_view(), name='profile'),

    # Invites.
    url(r'^invite/$', views.invite, name='invite'),

    # Get single post
    url(r'^post/get/(?P<pk>[0-9]+)/$', views.SinglePostView.as_view(), name='post_get'),

    # Get single thread
    url(r'^thread/get/(?P<pk>[0-9]+)/$', views.SingleThreadView.as_view(), name='thread_get'),

    # Update thread
    url(r'^(?P<board_name>[a-z]{1,3})/thread/update/(?P<thread_id>[0-9]+)/(?P<posts_numb>[0-9]+)$',
        views.ThreadUpdateView.as_view(), name='thread_update'),

    # Liked threads
    url(r'^liked/$', views.liked, name='liked'),

    # Error page.
    url(r'^closed/$', views.closed, name='closed'),

    # Details page.
    url(r'^other/$', views.other, name='other'),
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