from django.contrib import admin

from .models import Conversation, Category, Limits, Comment, Vote

register = (lambda model: lambda cfg: admin.site.register(model, cfg) or cfg)


class VoteInline(admin.TabularInline):
    model = Vote


@register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fields = ['conversation', 'author', 'content', 'status', 'rejection_reason']
    list_display = ['id', 'content', 'conversation', 'created', 'status']
    list_editable = ['status', ]
    list_filter = ['conversation', 'status']
    inlines = [VoteInline]


@register(Limits)
class LimitsAdmin(admin.ModelAdmin):
    pass


@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ['name', 'image', 'image_caption']
    list_display = ['id', 'name', 'slug', 'created', 'modified']


@register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    fields = ['author', 'title', 'description', 'is_promoted', 'category', 'nudge_limit']
    list_display = ['slug', 'title', 'author', 'created', 'modified']
    list_filter = ['is_promoted']
