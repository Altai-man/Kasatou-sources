# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import RedirectView, ListView, DetailView, TemplateView
from django.conf import settings

# Kasatou modules
from Layers.models import Thread


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['threads'] = Thread.objects.all()[:5]
        return context