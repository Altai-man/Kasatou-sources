"""Description of Kasatou views."""
# Django modules
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseRedirect, HttpResponseForbidden
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
from Layers.utils import return_user


class BaseBoardClass(ContextMixin):
    """Board dispatcher."""
    def dispatch(self, *args, **kwargs):
        """Dispatch method."""
        # Current board.
        if 'board_name' in kwargs.keys():
            self.board = get_object_or_404(Board.objects,
                                           board_name=kwargs['board_name'])
        else:
            self.board = None

        return super(BaseBoardClass, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get context."""
        user = return_user(self.request)

        context = super(BaseBoardClass, self).get_context_data(**kwargs)
        context['board'] = self.board
        context['boards'] = Board.objects.all()
        context['user'] = user
        return context


class IndexView(TemplateView, BaseBoardClass):
    """View of index page."""
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Overloaded get_context_data for list of last threads."""
        context = super(IndexView, self).get_context_data(**kwargs)
        threads = Thread.objects.all().order_by('-update_time')[:6]
        try:
            # If we receive empty list, exception will raised
            context['main_thread'] = threads[0]
            context['main_posts'] = Post.objects.filter(
                thread_id=threads[0].pk).order_by('-date')[:3]
        except IndexError:
            context['main_thread'] = None

        context['threads'] = threads[1:6]
        # Slice from empty list is empty list.
        return context


class BoardView(ListView, BaseBoardClass):
    """View of Board page."""
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
    """View of Thread page."""
    model = Thread
    template_name = 'thread.html'
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        context = super(ThreadView, self).get_context_data(**kwargs)
        context['post_form'] = PostForm()
        context['posts'] = Post.objects.filter(thread_id=context['object']).order_by('pk')
        return context


class SingleThreadView(JsonMixin, DetailView):
    model = Thread
    context_object_name = 'thread'
    template_name = 'parts/thread.html'

    def render_to_response(self, context, **kwargs):
        context.update(thread_hide_answer=True)
        data = super(SingleThreadView,
                     self).render_to_response(context, **kwargs)
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
        posts = Post.objects.filter(thread_id__id=thread_id).order_by('date')[count:]
        return posts

    def render_to_response(self, context, **kwargs):
        is_new = True if context[self.context_object_name] else False
        response = dict(is_new=is_new)
        if is_new:
            posts = super(ThreadUpdateView,
                          self).render_to_response(context, **kwargs)
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
            return render_to_response(
                '404.html',
                {'text': 'Invite is outdated or already in use.'},
                context)

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

        return render_to_response(
            '404.html',
            {'text': "Sorry, but you have an errors in registration form."},
            {})


class Profile(View):
    @staticmethod
    def get(request):
        context = RequestContext(request)
        user = return_user(request)
        context['user'] = user
        return render_to_response("profile.html", {}, context)

    def post(self, request):
        context = RequestContext(request)
        user = return_user(request)
        user.theme = request.POST.get('theme', None)
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
                messages.error(request, 'You are banned.')
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


class PostCreating(View):
    @staticmethod
    def post(request, **kwargs):
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save()
            PostCreating.update_thread_attrs(
                kwargs['thread_id'], post_form.instance.date)
            post.save()
            return HttpResponse("OK")
        else:
            html = post_form.errors.as_ul()
            return HttpResponseBadRequest(html)

    @staticmethod
    def update_thread_attrs(t_id, date):
        cur_th = Thread.objects.select_related('board_id').get(pk=t_id)
        # Because we sort threads on board by update_time.
        if cur_th.post_count < cur_th.board_id.thread_max_post:
            cur_th.update_time = date
        cur_th.post_count += 1
        cur_th.save()


class PostDeleting(View):
    @staticmethod
    def post(request, p_id):
        try:
            post = Post.objects.get(pk=p_id)
        except:
            return HttpResponseBadRequest()
        thread = Thread.objects.get(pk=post.get_thread_id())
        user = return_user(request)

        if user == post.user_id or user.is_admin:
            post.delete()
            thread.post_count -= 1
            thread.save()
            return HttpResponse("OK")
        else:
            return HttpResponseForbidden()


class PostEditing(View):
    @staticmethod
    def get(request, p_id):
        context = RequestContext(request)
        user = return_user(request)
        try:
            post = Post.objects.select_related('user_id').get(pk=p_id)
            if post.user_id.pk is not user.pk:
                return HttpResponseRedirect("/")
            context['raw_text'] = Post.unmarkup(post.text)
            context['post'] = post
            context['thread_id'] = post.get_thread_id()
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
        addr = '/'.join(('',
                         request.POST['board_name'],
                         'thread',
                         request.POST['thread_id'],
                         '#post_' + p_id))
        return HttpResponseRedirect(addr)


def invite(request):
    context = RequestContext(request)
    user = return_user(request)

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
        context['invite_link'] = \
                                 "Sorry, you don't have any invites right now."

    return render_to_response("profile.html", {}, context)


def closed(request):
    context = RequestContext(request)
    return render_to_response("closed.html", {}, context)
