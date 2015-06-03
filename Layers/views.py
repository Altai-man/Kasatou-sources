# -*- coding: utf-8 -*-

# Django modules
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import View, ListView, DetailView
from django.views.generic.base import TemplateView, ContextMixin

# Kasatou modules
from Layers.models import Board
from Layers.models import Invite
from Layers.models import Post
from Layers.forms import PostForm
from Layers.models import Thread
from Layers.forms import ThreadForm
from Layers.forms import UserForm
from Layers.mixins import JsonMixin
from Layers.snippets import get_obj_or_none
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
        context['threads'] = Thread.objects.all().order_by('-update_time')[:10]
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


class Register(View):
    @staticmethod
    def get(request, code):
        try:
            invitation = Invite.objects.get(code=code)
        except Invite.DoesNotExist:
            return HttpResponseRedirect("/")

        context = RequestContext(request)
        if invitation is None:
            return render_to_response('404.html', context)
        if invitation.is_active:
            user_form = UserForm()
            invitation.is_active = False
            invitation.save()

            return render_to_response(
                'register.html',
                {'user_form': user_form}, context)
        else:
            return render_to_response('404.html', {'text': 'Invite is outdated or already in use.'}, context)

    @staticmethod
    def post(request):
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            user = authenticate(email=request.POST['email'],
                                password=request.POST['password'])
            login(request, user)
            return HttpResponseRedirect("/")

        return render_to_response('404.html',
                                  {'text': "Sorry, but you have an errors in registration form."}, {})


class Profile(View):
    @staticmethod
    def get_user(key):
        session = Session.objects.get(session_key=key)
        uid = session.get_decoded().get('_auth_user_id')
        return User.objects.get(pk=uid)

    def get(self, request):
        context = RequestContext(request)
        session_key = request.session.session_key
        user = self.get_user(session_key)

        context['user'] = user
        return render_to_response("profile.html", {}, context)

    def post(self, request):
        context = RequestContext(request)
        session_key = request.session.session_key
        user = self.get_user(session_key)
        user.name = request.POST.get('name', None)
        user.theme = request.POST.get('theme', None)
        user.liked_threads = request.POST.get('liked_threads', None)
        user.thread_per_page = request.POST.get('thread_per_page', None)

        user.save()
        context['user'] = user
        return render_to_response("profile.html", {}, context)


class Login(View):
    @staticmethod
    def post(request):
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

    @staticmethod
    def get(request):
        context = RequestContext(request)
        return render_to_response('login.html', {}, context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


class SearchView(View):
    @staticmethod
    def post(request):
        search_text = request.POST['search_text']
        context = RequestContext(request)
        context.update({
            'posts': Post.objects.search(search_text)
        })
        return render_to_response('search.html', {}, context)

    @staticmethod
    def get(request):
        context = RequestContext(request)
        return render_to_response("search.html", {}, context)


class ThreadCreating(View):
    @staticmethod
    def post(request):
        board_id = request.POST.get('board_id')
        board_name = Board.objects.get(id=board_id)
        addr = ''.join([str(board_name)])

        thread_form = ThreadForm(request.POST, request.FILES)

        if thread_form.is_valid():
            thread = thread_form.save()
            thread.save()
            return HttpResponseRedirect(addr)
        else:
            messages.error(request, thread_form.errors)
            return HttpResponseRedirect(addr)


def post_adding(request, **kwargs):
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
    post = Post.objects.get(pk=p_id)
    board_name = str(post.board_id)
    thread = Thread.objects.get(pk=post.get_id())
    addr = ''.join([str(board_name), "thread/", str(post.get_id())])

    if request.method == 'GET':
        session_key = request.session.session_key

        session = Session.objects.get(session_key=session_key)
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)

        post = get_obj_or_none(Post, id=p_id)
        if user == post.user_id or user.is_admin:
            if post is not None:
                post.delete()
                thread.post_count -= 1
                thread.save()
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


class PostEditing(View):
    @staticmethod
    def get(request, p_id):
        context = RequestContext(request)
        try:
            post = Post.objects.get(pk=p_id)
            context['raw_text'] = Post.unmarkup(post.text)
            context['post'] = post
            context['thread_id'] = post.get_id()
            board = Board.objects.get(pk=post.board_id.pk)
            context['board_name'] = board.board_name
        except Post.DoesNotExist:
            return HttpResponseRedirect("/")
        return render_to_response("edit.html", {}, context)

    @staticmethod
    def post(request, p_id):
        try:
            post = Post.objects.get(pk=p_id)
        except Post.DoesNotExist:
            return HttpResponseRedirect("/")
        post.text = Post.markup(request.POST['text'])
        post.topic = request.POST['topic']
        post.save()
        addr = '/'.join(('', request.POST['board_name'], 'thread', request.POST['thread_id'], '#post_' + p_id))
        return HttpResponseRedirect(addr)


def invite(request):
    context = RequestContext(request)
    session_key = request.session.session_key
    session = Session.objects.get(session_key=session_key)
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)

    if user.invites_count > 0:
        i = Invite()
        i.sender = user
        i.generate_code()
        link = 'http://kasatou.ru/register/' + i.code
        context['invite_link'] = link
        i.save()
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
        thread = get_obj_or_none(Thread, id=th)
        if thread is not None:
            context['liked'].append(thread)
    return render_to_response("liked.html", {}, context)


def closed(request):
    context = RequestContext(request)
    return render_to_response("closed.html", {}, context)


def other(request):
    context = RequestContext(request)
    return render_to_response("other.html", {}, context)


def last(request):
    context = RequestContext(request)
    context['posts'] = Post.objects.all().order_by('-date')[:5]
    return render_to_response("parts/last_posts.html", {}, context)
