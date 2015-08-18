from Layers import views
from django.conf.urls import patterns, url

user_patterns = patterns(
    '',

    url(r'^login/$', views.Login.as_view(), name='login'),

    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^profile/$', views.Profile.as_view(), name='profile'),

    # Invites.
    url(r'^invite/$', views.invite, name='invite'),

    # Urls for auth pages
    url(r'^register/(?P<code>.*)/$', views.Register.as_view(), name='register_get'),
    url(r'^register/$', views.Register.as_view(), name='register_accept'),
)
