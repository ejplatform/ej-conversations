from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers

from .mixins import HasAuthorSerializer, HasLinksSerializer
from .models import Category, Conversation, Comment, Vote


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username')
        extra_kwargs = {'url': {'lookup_field': 'username'}}


class CategorySerializer(HasLinksSerializer):
    class Meta:
        model = Category
        fields = ('links', 'name', 'slug', 'image', 'image_caption')
        extra_kwargs = {'url': {'lookup_field': 'slug'}}


class ConversationSerializer(HasAuthorSerializer):
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('links', 'title', 'slug', 'description', 'author_name',
                  'created', 'modified', 'is_promoted', 'category', 'statistics')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
            'category': {'lookup_field': 'slug'},
        }

    def get_inner_links(self, obj):
        return ['user_data', 'votes', 'approved_comments', 'random_comment']

    def get_statistics(self, obj):
        # FIXME: for some reason DRF calls this method 4 times when
        # serializing data. This behavior puts the database into a crawl
        print('stats!')
        try:
            return obj._statistics
        except AttributeError:
            obj._statistics = statistics = obj.get_statistics()
            return statistics


class CommentSerializer(HasAuthorSerializer):
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('links', 'id', 'content', 'author_name',
                  'status', 'created', 'modified', 'rejection_reason',
                  'conversation', 'statistics')
        read_only_fields = ('id', 'author', 'status', 'rejection_reason')
        extra_kwargs = {
            'category': {'lookup_field': 'slug'},
            'conversation': {'write_only': True, 'lookup_field': 'slug'},
        }

    def get_inner_links(self, obj):
        return ['vote']

    def get_links(self, obj):
        payload = super().get_links(obj)
        payload['conversation'] = self.url_prefix + reverse(
            'conversation-detail', kwargs={'slug': obj.conversation.slug}
        )
        return payload

    def create(self, validated_data):
        conversation = validated_data.pop('conversation')
        return conversation.create_comment(**validated_data)

    def get_statistics(self, obj):
        return obj.get_statistics()


class VoteSerializer(HasLinksSerializer):
    comment_text = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ('links', 'comment_text', 'action', 'comment', 'value')
        extra_kwargs = {
            'comment': {'write_only': True},
            'value': {'write_only': True},
        }

    def get_links(self, obj):
        payload = super().get_links(obj)
        path = reverse('comment-detail', kwargs={'pk': obj.comment.pk})
        payload['comment'] = self.url_prefix + path
        return payload

    def get_comment_text(self, obj):
        return obj.comment.content

    def get_action(self, obj):
        return Vote.VOTE_NAMES[obj.value]

    def create(self, data):
        comment = data.pop('comment')
        return comment.vote(**data)
