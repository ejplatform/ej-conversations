from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers
from .models import Category, Conversation, Comment, Vote
from .permissions import IsAdminOrReadOnly


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = get_user_model().objects.all()
    lookup_field = 'username'


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ConversationSerializer
    queryset = Conversation.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['is_promoted', 'category_id']
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True)
    def user_data(self, request, slug):
        conversation = self.get_object()
        return Response(conversation.get_user_data(request.user))

    @action(detail=True)
    def votes(self, request, slug):
        conversation = self.get_object()
        votes = conversation.get_votes(request.user)
        serializer = serializers.VoteSerializer(votes, many=True,
                                                context={'request': request})
        return Response(serializer.data)

    @action(detail=True)
    def approved_comments(self, request, slug):
        conversation = self.get_object()
        comments = conversation.get_comments()
        serializer = serializers.CommentSerializer(
            comments, many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True)
    def random_comment(self, request, slug):
        conversation = self.get_object()
        try:
            comment = conversation.get_next_comment(request.user)
        except Comment.DoesNotExist as msg:
            return Response({
                "message": str(msg),
                "error": True,
            })
        ctx = {'request': request}
        serializer = serializers.CommentSerializer(comment, context=ctx)
        return Response(serializer.data)

    @action(detail=False)
    def random(self, request):
        try:
            conversation = Conversation.objects.random(request.user)
        except Conversation.DoesNotExist as msg:
            return Response({
                "message": str(msg),
                "error": True,
            })
        ctx = {'request': request}
        serializer = serializers.ConversationSerializer(conversation, context=ctx)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['status', 'conversation__slug']
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except PermissionError as err:
            return Response(err.args[0])


class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.VoteSerializer
    queryset = Vote.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['comment__conversation__slug']
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return self.queryset.filter(author_id=user.id)
        else:
            return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
