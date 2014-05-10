from django.conf.urls import *
from django.views.generic.simple import direct_to_template

from registration.forms import RegistrationFormTermsOfService
from invitation.views import invite, invited, register
from invitation.forms import InvitationKeyForm, MultiInvitationKeyForm

urlpatterns = patterns('',
                       url(r'^invitation/invite$',
                           invite,
                           { 
                               'form_class': InvitationKeyForm,
                           },
                           name='invitation_invite'),
                       url(r'^invitation/bulk_invite$',
                           invite,
                           { 
                               'form_class': MultiInvitationKeyForm,
                           },
                           name='invitation_bulk_invite'),
                       url(r'', include('invitation.urls')),
                       url(r'', include('registration.backends.default.urls')),
)
