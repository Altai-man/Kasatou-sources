# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import RedirectView, ListView, DetailView, TemplateView
from django.conf import settings

# Kasatou modules
from Layers.models import Thread
from Layers.models import Post


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['threads'] = Thread.objects.all()[:5]
        return context

class BoardView(TemplateView):
    template_name = "board.html"

    def get_context_data(self, **kwargs):
        context = super(BoardView, self).get_context_data(**kwargs)
        context['threads'] = Thread.objects.all()
        context['threads_menu'] = Thread.objects.all().order_by('-update_time')[:6]
        context['posts'] = Post.objects.all()
        return context
