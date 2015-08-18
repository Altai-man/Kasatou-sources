#! -*- coding: utf-8 -*-
from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpResponseRedirect
from Layers.models import User
from django.conf import settings


class Invitation(object):
    @staticmethod
    def process_request(request):
        try:
            session_key = request.session.session_key
            pk = Session.objects.get(session_key=session_key).get_decoded().get('_auth_user_id')
            try:
                user = User.objects.get(pk=pk)
            except:
                user = None
        except Session.DoesNotExist:
            user = None

        if user is not None:
            return None
        elif "css" in request.path or "png" in request.path:
            return None
        elif user is None and request.path in settings.ALLOWED_PATHS:
            return None
        elif user is None and "/register/" in request.path:
            return None
        elif user is None and request.path != "/login/":
            return HttpResponseRedirect("/closed/")
        else:
            return HttpResponse("Sorry, something goes wrong with the server.")
