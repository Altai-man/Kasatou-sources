from Layers import views
from django.conf.urls import patterns, url

post_patterns = patterns(
    '',

    # Add post
    url(r'^(?P<board_name>[a-z]{1,3})/thread/(?P<thread_id>[0-9]+)/add_post/$',
        views.PostCreating.as_view(), name='post_add'),

    # Get single post
    url(r'^post/get/(?P<pk>[0-9]+)/$', views.SinglePostView.as_view(), name='post_get'),

    # Edit post
    url(r'post_editing/(?P<p_id>[0-9]+)', views.PostEditing.as_view()),

    # Remove post
    url(r'post_deleting/(?P<p_id>[0-9]+)', views.PostDeleting.as_view(), name='post_deleting'),
)
