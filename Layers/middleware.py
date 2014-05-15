#! -*- coding: utf-8 -*-
from django.contrib.sessions.models import Session
from Layers.snippets import get_obj_or_None
from django.http import HttpResponse
from Layers.models import User

class Invitation(object):
    def process_request(self, request):
        session_key = request.session.session_key
        session = Session.objects.get(session_key=session_key).get_decoded().get('_auth_user_id')
        user = get_obj_or_None(User, pk=session)

        if user != None:
            return None
        elif user == None and request.path == "/login/":
            return None
        elif user == None and request.path == "/register/":
            return None
        elif user == None and request.path == "/bunny/":
            return None
        elif user == None and request.path != "/login/":
            return HttpResponse("Sorry, you need to log in to view the board.")
        else:
            return HttpResponse("Sorry, something goes wrong with the server.")