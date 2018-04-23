from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Conversation, Category, Limits, Comment, Vote

register = (lambda model: lambda cfg: admin.site.register(model, cfg) or cfg)
SHOW_VOTES = getattr(settings, 'EJ_CONVERSATIONS_SHOW_VOTES', False)


class VoteInline(admin.TabularInline):
    model = Vote
    raw_id_fields = ['author']


class AuthorIsUserMixin(admin.ModelAdmin):
    def save_model(self, request, obj, *args, **kwargs):
        obj.author = request.user
        return super().save_model(request, obj, *args, **kwargs)


@register(Comment)
class CommentAdmin(AuthorIsUserMixin, admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['conversation', 'content']}),
        (_('Moderation'), {'fields': ['status', 'rejection_reason']}),
    ]
    list_display = ['content', 'conversation', 'created', 'status']
    list_editable = ['status']
    list_filter = ['conversation', 'status', 'created']

    if SHOW_VOTES:
        inlines = [VoteInline]


@register(Limits)
class LimitsAdmin(admin.ModelAdmin):
    add_form_template = 'admin/change_form.html'
    fieldsets = [
        (None,
         {'fields': ['description', 'interval']}),
        (_('Comements'),
         {'fields': ['max_comments_in_interval',
                     'max_comments_per_conversation']}),
        (_('Votes'),
         {'fields': ['max_votes_in_interval', 'max_votes_per_conversation']}),
    ]


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'image', 'image_caption']
    list_display = ['name', 'slug', 'created', 'has_image']
    list_filter = ['created', 'modified']

    def has_image(self, obj):
        has_image = obj.image is not None
        return _('yes') if has_image else _('no')


@register(Conversation)
class ConversationAdmin(AuthorIsUserMixin, admin.ModelAdmin):
    fields = ['title', 'question', 'category', 'is_promoted']
    list_display = ['title', 'slug', 'author', 'created']
    list_filter = ['is_promoted', 'created', 'category__name']
