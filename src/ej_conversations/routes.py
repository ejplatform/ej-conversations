from django.http import Http404, HttpResponseServerError
from django.shortcuts import get_object_or_404, render

from boogie.router import Router
from . import models

urlpatterns = Router()


@urlpatterns.route('')
def conversation_list(request):
    ctx = {
        'conversations': models.Conversation.objects.all(),
        'categories': models.Category.objects.all(),
    }
    return render(request, 'pages/conversation-list.jinja2', ctx)


@urlpatterns.route('<slug:slug>/')
def category_list(request, slug):
    category = get_object_or_404(models.Category, slug=slug)
    ctx = dict(
        category=category,
        categories=models.Category.objects.all(),
        conversations=category.conversations.all(),
    )
    return render(request, 'pages/category-detail.jinja2', ctx)


@urlpatterns.route('<slug:category_slug>/<slug:slug>/')
def conversation_detail(request, slug, category_slug):
    conversation = get_object_or_404(models.Conversation, slug=slug)
    if conversation.category.slug != category_slug:
        raise Http404
    comment = conversation.get_next_comment(request.user, None)
    ctx = {
        'conversation': conversation,
        'comment': comment,
    }
    if comment and request.POST.get('action') == 'vote':
        vote = request.POST['vote']
        if vote not in {'agree', 'skip', 'disagree'}:
            return HttpResponseServerError('invalid parameter')
        comment.vote(request.user, vote)
    elif request.POST.get('action') == 'comment':
        comment = request.POST['comment'].strip()
        conversation.create_comment(request.user, comment)

    return render(request, 'pages/conversation-detail.jinja2', ctx)


@urlpatterns.route('<slug:category_slug>/<slug:slug>/info/')
def conversation_info(request, slug, category_slug):
    conversation = get_object_or_404(models.Conversation, slug=slug)
    if conversation.category.slug != category_slug:
        raise Http404

    ctx = dict(
        conversation=conversation,
        info=conversation.get_statistics(),
    )
    return render(request, 'pages/conversation-info.jinja2', ctx)
