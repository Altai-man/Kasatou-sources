# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import RedirectView, ListView, DetailView
from django.views.generic.base import TemplateView, ContextMixin
from django.conf import settings

# Kasatou modules
from Layers.models import Thread
from Layers.models import Post
from Layers.models import Board


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['threads'] = Thread.objects.all()[:5]
        return context


class BaseBoardClass(ContextMixin):
    def dispatch(self, *args, **kwargs):
        # Current board. Doing it here because sometimes I need it before get_context_data
        if 'board_name' in kwargs.keys():
            self.board = get_object_or_404(Board.objects, board_name=kwargs['board_name'])
        else:
            self.board = None

        return super(BaseBoardClass, self).dispatch(*args, **kwargs)

    def get_context_data(self,**kwargs):
        context = super(BaseBoardClass,self).get_context_data(**kwargs)
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
        context['threads_menu'] = Thread.objects.all().order_by('-update_time')[:6]
        return context

class ThreadView(DetailView, BaseBoardClass):
    model = Thread
    template_name = 'thread.html'
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        context = super(ThreadView,self).get_context_data(**kwargs)
#        context['post_form'] = PostForm()
        context['posts'] = Post.objects.filter(thread_id=context['object'])

        # Hide "Answer" button
        context['thread_hide_answer'] = True

        return context