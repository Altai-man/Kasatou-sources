# -*- coding: utf-8 -*-

# Django modules
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import RedirectView, ListView, DetailView
from django.views.generic.base import TemplateView, ContextMixin

# Kasatou modules
from Layers.models import BasePost
from Layers.models import Board
from Layers.models import Invite
from Layers.models import Post
from Layers.models import PostForm
from Layers.models import Thread
from Layers.models import ThreadForm
from Layers.models import UserForm
from Layers.mixins import JsonMixin, JsonFormMixin
from Layers.snippets import get_obj_or_None
User = get_user_model()


class BaseBoardClass(ContextMixin):
    def dispatch(self, *args, **kwargs):
        # Current board.
        if 'board_name' in kwargs.keys():
            self.board = get_object_or_404(Board.objects,
                                           board_name=kwargs['board_name'])
        else:
            self.board = None

        return super(BaseBoardClass, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        s_key = self.request.session.session_key
        session = Session.objects.get(session_key=s_key).get_decoded()
        uid = session.get('_auth_user_id')
        user = User.objects.get(pk=uid)

        context = super(BaseBoardClass, self).get_context_data(**kwargs)
        context['board'] = self.board
        context['boards'] = Board.objects.all()
        context['user'] = user
        return context


class IndexView(TemplateView, BaseBoardClass):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['threads'] = reversed(Thread.objects.all().order_by('-update_time')[:10])
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


class SingleThreadView(JsonMixin, DetailView):
    model = Thread
    context_object_name = 'thread'
    template_name = 'parts/thread.html'

    def render_to_response(self, context, **kwargs):
        context.update(thread_hide_answer=True)
        data = super(SingleThreadView, self).render_to_response(context, **kwargs)
        response = dict(answer=data.rendered_content)
        return self.render_json_answer(response)

class SinglePostView(SingleThreadView):
    model = Post
    context_object_name = 'post'
    template_name = 'parts/post.html'


class ThreadUpdateView(JsonMixin, ListView):
    model = Post
    template_name = "parts/posts.html"
    context_object_name = "posts"

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        count = int(self.kwargs['posts_numb'])
        posts = Post.objects.filter(thread_id__id=thread_id)[count:]
        return posts

    def render_to_response(self, context, **kwargs):
        is_new = True if context[self.context_object_name] else False
        response = dict(is_new=is_new)
        if is_new:
            posts = super(ThreadUpdateView, self).render_to_response(context, **kwargs)
            response.update(new_threads=posts.rendered_content)
        return self.render_json_answer(response)


def register_get(request, invite):
    context = RequestContext(request)

    try:
        invite = Invite.objects.get(code=invite)
    except:
        invite = None

    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    else:
        if request.method == 'GET':
            if invite is None:
                return render_to_response('404.html', context)
            else:
                if invite.is_active:
                    user_form = UserForm()
                    invite.is_active = False
                    invite.save()

                    return render_to_response(
                        'register.html',
                        {'user_form': user_form}, context)
                else:
                    return render_to_response('404.html', {'text': 'Invite is outdated or already in use.'}, context)
        else:
            HttpResponseRedirect("/")


def register_accept(request):
    context = RequestContext(request)

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return render_to_response('404.html', {'text': "Sorry, but you have an errors in registration form."}, context)
    else:
        return HttpResponseRedirect("/login/")


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
        liked_threads = request.POST.get('liked_threads')
        thread_per_page = request.POST.get('thread_per_page')
        user.name = name
        user.theme = theme
        user.liked_threads = liked_threads
        user.thread_per_page = thread_per_page

        user.save()

        return render_to_response("profile.html", {}, context)


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)

        if user:

            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')

            else:
                messages.error(request,
                               """You are banned.
                               If you want to use imageboard - please, contact administrator.""")
                return HttpResponseRedirect("/login/")

        else:
            messages.error(request, "Data is wrong. Are you registered?")
            return HttpResponseRedirect("/login/")

    else:
        return render_to_response('login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


def search(request):
    context = RequestContext(request)

    if request.method == 'POST':
        search_text = request.POST['search_text']
        posts = BasePost.objects.search(search_text)

        context.update({
            'posts': BasePost.objects.search(search_text)
        })
        return render_to_response('search.html', {}, context)

    else:
        return render_to_response("search.html", {}, context)


def create_thread(request, **kwargs):
    context = RequestContext(request)
    board_id = request.POST.get('board_id')
    board_name = Board.objects.get(id=board_id)
    addr = ''.join([str(board_name)])

    if request.method == 'POST':
        thread_form = ThreadForm(request.POST, request.FILES)

        if thread_form.is_valid():
            thread = thread_form.save()
            thread.save()
            return HttpResponseRedirect(addr)

        else:
            messages.error(request, thread_form.errors)
            return HttpResponseRedirect(addr)

    else:
        return HttpResponseRedirect(addr)


def post_adding(request, **kwargs):
    context = RequestContext(request)
    board_id = request.POST.get('board_id')
    board_name = Board.objects.get(id=board_id)
    thread_id = request.POST.get('thread_id')
    addr = ''.join([str(board_name), "thread/", str(thread_id)])

    if request.method == 'POST':
        text = request.POST.get('text')
        topic = request.POST.get('topic')
        image1 = request.FILES.get('image1')

        post_form = PostForm(request.POST, request.FILES)


        if post_form.is_valid():
            if text or topic or image1:  # We do not save empty posts.
                post = post_form.save()

                # Update thread attributes.
                current_thread = get_object_or_404(Thread.objects, id=thread_id)
                current_board = get_object_or_404(Board.objects, id=board_id)
                if current_thread.post_count < current_board.thread_max_post:
                    current_thread.update_time = post_form.instance.date

                current_thread.post_count += 1

                # Save thread.
                current_thread.save()
                # Save post.
                post.save()

                return HttpResponseRedirect(addr)
            else:
                messages.error(request,
                               "Message should have image or text or topic.")
                return HttpResponseRedirect(addr)

        else:
            messages.error(request, post_form.errors)
            return HttpResponseRedirect(addr)

    else:
        return HttpResponseRedirect(addr)


def post_deleting(request, p_id):
    board_name = str(Post.objects.get(id=p_id).board_id)
    thread_id = Post.objects.get(id=p_id).get_id()
    addr = ''.join([str(board_name), "thread/", str(thread_id)])

    if request.method == 'GET':
        session_key = request.session.session_key

        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)

        post = get_obj_or_None(Post, id=p_id)
        if user == post.user_id or user.is_admin:
            if post is not None:
                post.delete()
                return HttpResponseRedirect(addr)
            else:
                messages.error(request,
                               "<script>alert('Sorry, but this message doesn't exist.');</script>")
                return HttpResponseRedirect(addr)
        else:
                messages.error(request,
                               "<script>alert('Sorry, but you have not enough permissions.');</script>")
                return HttpResponseRedirect(addr)
    else:
        return HttpResponseRedirect(addr)

def invite(request):
    context = RequestContext(request)
    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)

    if user.invites_count > 0:
        invite = Invite()
        invite.sender = user
        invite.generate_code()
        link = 'http://kasatou.ru/register/' + invite.code
        context['invite_link'] = link
        invite.save()
        user.invites_count -= 1
        user.save()
    else:
        context['invite_link'] = "Sorry, but you don't have any invites right now."

    return render_to_response("profile.html", {}, context)

def liked(request):
    context = RequestContext(request)
    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)

    threads = user.liked_threads
    ids = threads.split(";")
    context['liked'] = []

    for th in ids:
        thread = get_obj_or_None(Thread, id=th)
        if thread != None:
            context['liked'].append(thread)
    return render_to_response("liked.html", {}, context)

def closed(request):
    context = RequestContext(request)
    return render_to_response("closed.html", {}, context)