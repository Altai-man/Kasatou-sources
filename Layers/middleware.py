#! -*- coding: utf-8 -*-
from django.contrib.sessions.models import Session
from Layers.snippets import get_obj_or_None
from django.http import HttpResponse, HttpResponseRedirect
from Layers.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext
from Kasatou.settings import CLOSED

class Invitation(object):
    def process_request(self, request):
        if CLOSED:
            if "css" in request.path or "png" in request.path:
                return None
            else:
                context = RequestContext(request)
                return render_to_response("404.html", {"soon": "Coming soon!"}, context)
        else:
            try:
                session_key = request.session.session_key
                session = Session.objects.get(session_key=session_key).get_decoded().get('_auth_user_id')
                user = get_obj_or_None(User, pk=session)
            except:
                user = None
            if user != None:
                return None
            elif "css" in request.path or "png" in request.path:
                return None
            elif user == None and request.path == "/login/":
                return None
            elif user == None and "/register/" in request.path:
                return None
            elif user == None and request.path == "/bunny/":
                return None
            elif user == None and request.path != "/login/":
                return HttpResponse("Sorry, you need to log in to view the board.")
            else:
                return HttpResponse("Sorry, something goes wrong with the server.")