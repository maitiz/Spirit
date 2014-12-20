# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render

from spirit.utils.decorators import administrator_required
from spirit.models.topic import Topic


@administrator_required
def topic_deleted(request):
    # Private topics cant be deleted, closed or pinned so we are ok
    topics = Topic.objects.filter(is_removed=True)
    return render(request, 'spirit/admin/topic/topic_deleted.html', {'topics': topics, })


@administrator_required
def topic_closed(request):
    topics = Topic.objects.filter(is_closed=True)
    return render(request, 'spirit/admin/topic/topic_closed.html', {'topics': topics, })


@administrator_required
def topic_pinned(request):
    topics = Topic.objects.filter(is_pinned=True) | Topic.objects.filter(is_globally_pinned=True)
    return render(request, 'spirit/admin/topic/topic_pinned.html', {'topics': topics, })
