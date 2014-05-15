#! -*- coding: utf-8 -*-
from django.shortcuts import _get_queryset

def get_obj_or_None(cls, *args, **kwargs):
    queryset = _get_queryset(cls)
    try:
        return queryset.get(*args, **kwargs)
    except:
        return None