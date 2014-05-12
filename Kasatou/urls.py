from django.conf.urls import patterns, include, url
from Layers import views
from django.contrib import admin
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
    url(r'^search/$', views.search, name='search'),

    # Add thread
    url(r'^thread_add/$', views.create_thread, name='thread_add'),

    # Add post
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<thread_id>[0-9]+)/add_post$',views.post_adding, name='post_add'),

    # Urls for auth pages
    url(r'^register/$', views.register, name='register'),

    url(r'^login/$', views.user_login, name='login'),

    url(r'^logout/$', views.user_logout, name='logout'),

   # Move to post
#    url(r'^post/(?P<pk>[0-9]+)/$',views.PostView.as_view(),name='post_view'),

    # Get single post
#    url(r'^post/get/(?P<pk>[0-9]+)/$',views.SinglePostView.as_view(),name='post_get'),

    # Get single thread
#    url(r'^thread/get/(?P<pk>[0-9]+)/$',views.SingleThreadView.as_view(),name='thread_get'),

    # Update thread
#    url(r'^(?P<board_name>[a-z]{1,3})/thread/update/(?P<thread_id>[0-9]+)/(?P<posts_numb>[0-9]+)$',views.ThreadUpdateView.as_view(),name='thread_update'),

 

    # Invites.
#    url(r'^invite/', include('invite_registration.urls')),

    # Accounts.
#    url(r'^accounts/', include('invite_registration.backends.invite_only.urls')),
)
