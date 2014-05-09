# -*- coding: utf-8 -*-

# Django modules
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from django.views.generic import RedirectView, ListView, DetailView, View
from django.conf import settings

# Kasatou modules
from Layers import models

