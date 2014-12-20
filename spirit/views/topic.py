# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponsePermanentRedirect
from django.conf import settings

from spirit.utils.ratelimit.decorators import ratelimit
from spirit.models.category import Category
from spirit.models.comment import MOVED
from spirit.forms.comment import CommentForm
from spirit.signals.comment import comment_posted
from spirit.forms.topic_poll import TopicPollForm, TopicPollChoiceFormSet

from spirit.models.topic import Topic
from spirit.forms.topic import TopicForm
from spirit.signals.topic import topic_viewed
from spirit.signals.topic_moderate import topic_post_moderate


@login_required
@ratelimit(rate='1/10s')
def topic_publish(request, category_id=None):
    if category_id:
        Category.objects.get_public_or_404(pk=category_id)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST)
        cform = CommentForm(user=request.user, data=request.POST)
        pform = TopicPollForm(data=request.POST)
        pformset = TopicPollChoiceFormSet(can_delete=False, data=request.POST)

        if not request.is_limited and form.is_valid() and cform.is_valid() \
                and pform.is_valid() and pformset.is_valid():
            # wrap in transaction.atomic?
            topic = form.save()

            cform.topic = topic
            comment = cform.save()
            comment_posted.send(sender=comment.__class__, comment=comment, mentions=cform.mentions)

            # Create a poll only if we have choices
            if pformset.is_filled():
                pform.topic = topic
                poll = pform.save()
                pformset.instance = poll
                pformset.save()

            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(user=request.user, initial={'category': category_id, })
        cform = CommentForm()
        pform = TopicPollForm()
        pformset = TopicPollChoiceFormSet(can_delete=False)

    return render(request, 'spirit/topic/topic_publish.html', {'form': form, 'cform': cform,
                                                               'pform': pform, 'pformset': pformset})


@login_required
def topic_update(request, pk):
    topic = Topic.objects.for_update_or_404(pk, request.user)

    if request.method == 'POST':
        form = TopicForm(user=request.user, data=request.POST, instance=topic)
        category_id = topic.category_id

        if form.is_valid():
            topic = form.save()

            if topic.category_id != category_id:
                topic_post_moderate.send(sender=topic.__class__, user=request.user, topic=topic, action=MOVED)

            return redirect(request.POST.get('next', topic.get_absolute_url()))
    else:
        form = TopicForm(user=request.user, instance=topic)

    return render(request, 'spirit/topic/topic_update.html', {'form': form, })


def topic_detail(request, pk, slug):
    topic = Topic.objects.get_public_or_404(pk, request.user)

    if topic.slug != slug:
        return HttpResponsePermanentRedirect(topic.get_absolute_url())

    topic_viewed.send(sender=topic.__class__, request=request, topic=topic)

    return render(request, 'spirit/topic/topic_detail.html', {'topic': topic,
                                                              'COMMENTS_PER_PAGE': settings.ST_COMMENTS_PER_PAGE})


def topics_active(request):
    topics = Topic.objects.for_public().filter()\
        .order_by('-is_globally_pinned', '-last_active')\
        .select_related('category')
    categories = Category.objects.for_parent()

    return render(request, 'spirit/topic/topics_active.html', {'categories': categories,
                                                               'topics': topics})
