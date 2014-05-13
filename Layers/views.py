# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.views.generic import RedirectView, ListView, DetailView
from django.views.generic.base import TemplateView, ContextMixin
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
User = get_user_model()

from django.conf import settings

# Kasatou modules
from Layers.models import Thread
from Layers.models import Post
from Layers.models import Board
from Layers.models import PostForm
from Layers.models import ThreadForm
from Layers.models import UserForm


class IndexView(TemplateView):
    template_name = "index.html"



    def get_context_data(self, **kwargs):
        session_key = self.request.session.session_key
        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)

        context = super(IndexView, self).get_context_data(**kwargs)
        context['threads'] = Thread.objects.all()[:5]
        context['user'] = user
        return context


class BaseBoardClass(ContextMixin):
    def dispatch(self, *args, **kwargs):
        # Current board.
        if 'board_name' in kwargs.keys():
            self.board = get_object_or_404(Board.objects, board_name=kwargs['board_name'])
        else:
            self.board = None

        return super(BaseBoardClass, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseBoardClass, self).get_context_data(**kwargs)
        context['board'] = self.board
        context['boards'] = Board.objects.all
        return context


class BoardView(ListView, BaseBoardClass):
    model = Thread
    template_name = "board.html"
    context_object_name = "threads"

    def get_queryset(self):
        return self.board.get_board_view()

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        context['thread_form'] = ThreadForm()
        context['threads_menu'] = Thread.objects.all().order_by('-update_time')[:6]
        return context


class ThreadView(DetailView, BaseBoardClass):
    model = Thread
    template_name = 'thread.html'
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        context = super(ThreadView, self).get_context_data(**kwargs)
        context['post_form'] = PostForm()
        context['posts'] = Post.objects.filter(thread_id=context['object'])

        return context


def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            profile.save()

            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
        'register.html',
        {'user_form': user_form, 'profile_form': profile_form,
         'registered': registered}, context)


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("You are banned.")
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render_to_response('login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/')


def search(request):
    context = RequestContext(request)

    if request.method == 'POST':
        search_text = request.POST['search_text']

        context.update({
            'posts': Post.objects.search(search_text),
        })
        return render_to_response('search.html', {}, context)

    else:
        return render_to_response("search.html", {}, context)


def create_thread(request, **kwargs):
    context = RequestContext(request)

    if request.method == 'POST':
        thread_form = ThreadForm(request.POST, request.FILES)

        if thread_form.is_valid():
            thread = thread_form.save()

            thread.save()
            return HttpResponseRedirect('/b/')
        else:
            print(thread_form.errors)
            return HttpResponse("Invalid thread details supplied.")

    else:
        return HttpResponseRedirect('/b/')


def post_adding(request, **kwargs):
    context = RequestContext(request)

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        thread_id = request.POST.get('thread_id')
        boardId = request.POST.get('board_id')
        board_list = Board.objects.filter(id=boardId).values('board_name').values_list()
        board_name = board_list[0][1]

        if post_form.is_valid():
            post = post_form.save()

            post.save()
            addr = "/" + board_name + "/thread/" + thread_id
            return HttpResponseRedirect(addr)
        else:
            print(post_form.errors)
            return HttpResponseRedirect('/b/')
    else:
        return HttpResponseRedirect('/b/')


def post_deleting(request, p_id):
    board_name = str(Post.objects.get(id=p_id).board_id)
    thread_name = Post.objects.get(id=p_id).thread_id
    thread_id = str(Thread.objects.get(topic=thread_name).id)
    addr = "" + board_name + "thread/" + thread_id

    if request.method == 'GET':
        session_key = request.session.session_key

        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)

        if user:
            if user.is_superuser:
                Post.objects.filter(id=p_id).delete()
                return HttpResponseRedirect(addr)
            else:
                return HttpResponseRedirect(addr)
    else:
        return HttpResponseRedirect(addr)


def profile(request):
    context = RequestContext(request)

    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)
    
    if request.method == 'GET':
        context.update({
            'user': user,
        })

        return render_to_response("profile.html", {}, context)
    else:
        name = request.POST.get('name')
        theme = request.POST.get('theme')
        thread_per_page = request.POST.get('thread_per_page')
        user.name = name
        user.theme = theme
        user.thread_per_page = thread_per_page

        user.save()

        return render_to_response("profile.html", {}, context)
