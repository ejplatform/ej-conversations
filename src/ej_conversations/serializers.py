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
        return ['user_data', 'votes', 'approved_comments']

    def get_statistics(self, obj):
        return obj.get_statistics()


class CommentSerializer(HasAuthorSerializer):
    class Meta:
        model = Comment
        fields = ('links', 'id', 'content', 'author_name',
                  'status', 'created', 'modified', 'rejection_reason',
                  'conversation')
        read_only_fields = ('id', 'author', 'status', 'rejection_reason')
        extra_kwargs = {
            'category': {'lookup_field': 'slug'},
            'conversation': {'write_only': True, 'lookup_field': 'slug'},
        }

    def get_links(self, obj):
        payload = super().get_links(obj)
        payload['conversation'] = self.url_prefix + reverse(
            'conversation-detail', kwargs={'slug': obj.conversation.slug}
        )
        return payload

    def create(self, validated_data):
        conversation = validated_data.pop('conversation')
        return conversation.create_comment(**validated_data)


class VoteSerializer(HasLinksSerializer):
    VOTE_VALUES = {
        Vote.AGREE: 'agree',
        Vote.DISAGREE: 'disagree',
        Vote.SKIP: 'skip',
    }
    comment_content = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ('links', 'id', 'value', 'comment_content', 'comment')
        extra_kwargs = {
            'comment': {'write_only': True}
        }

    def get_links(self, obj):
        payload = super().get_links(obj)
        payload['comment'] = self.url_prefix + reverse(
            'comment-detail', kwargs={'pk': obj.comment.pk}
        )
        return payload

    def get_comment_content(self, obj):
        return obj.comment.content

    def get_value(self, obj):
        return self.VOTE_VALUES[obj.value]
