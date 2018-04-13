from random import randrange

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .comment import Comment
from .limits import Limits
from .vote import Vote
from ..utils import CommentLimitStatus
from ..utils import custom_slugify
from .managers import ConversationManager

NOT_GIVEN = object()

BAD_LIMIT_STATUS = {CommentLimitStatus.BLOCKED,
                    CommentLimitStatus.TEMPORARILY_BLOCKED}


class Conversation(TimeStampedModel):
    """
    A topic of conversation.
    """

    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    description = models.TextField(
        _('Description'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        'Category',
        related_name='conversations',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    slug = AutoSlugField(
        unique=True,
        populate_from='title',
        slugify=custom_slugify,
    )
    is_promoted = models.BooleanField(
        _('Promoted'),
        default=False,
    )
    limits = models.ForeignKey(
        'Limits',
        related_name='conversations',
        on_delete=models.SET_NULL,
        blank=True, null=True,
    )
    style = models.ForeignKey(
        'ConversationStyle',
        related_name='conversations',
        on_delete=models.SET_NULL,
        blank=True, null=True,
    )

    objects = ConversationManager()
    votes = property(lambda self:
                     Vote.objects.filter(comment__conversation_id=self.id))

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # TODO: make this configurable!
        return '/conversations/' + self.slug

    def create_comment(self, author, content, commit=True, *,
                       check_limits=True,
                       **kwargs):
        """
        Create a new comment object for the given user.

        If commit=True (default), comment is persisted on the database.

        By default, this method check if the user can post according to the
        limits imposed by the conversation. It also normalizes duplicate
        comments and reuse duplicates from the database.
        """
        if check_limits:
            limit = self.get_limit_status(author)
            if limit in BAD_LIMIT_STATUS:
                raise PermissionError(CommentLimitStatus.MESSAGES[limit])

        make_comment = Comment.objects.create_or_update if commit else Comment
        return make_comment(author=author, content=content, **kwargs)

    def get_statistics(self):
        """
        Return a dictionary with basic statistics about conversation.
        """

        # Fixme: this takes several SQL queries. Maybe we can optimize later
        return dict(
            # Vote counts
            votes=dict(
                agree=vote_count(self, Vote.AGREE),
                disagree=vote_count(self, Vote.DISAGREE),
                skip=vote_count(self, Vote.SKIP),
                total=vote_count(self),
            ),

            # Comment counts
            comments=dict(
                approved=comment_count(self, Comment.STATUS.APPROVED),
                rejected=comment_count(self, Comment.STATUS.REJECTED),
                pending=comment_count(self, Comment.STATUS.PENDING),
                total=comment_count(self),
            ),

            # Participants count
            participants=get_user_model().objects
                .filter(votes__comment__conversation_id=self.id)
                .distinct()
                .count(),
        )

    def get_user_data(self, user):
        """
        Get information about user.
        """
        return dict(
            participation_ratio=self.get_participation_ratio(user),
        )

    def get_votes(self, user=None):
        """
        Get all votes for the conversation.

        If a user is supplied, filter votes for the given user.
        """
        kwargs = {'author_id': user.id} if user else {}
        return Vote.objects.filter(comment__conversation_id=self.id, **kwargs)

    def get_comments(self):
        """
        Return a sequence of all approved comments for conversation.
        """
        return self.comments.filter(status=Comment.STATUS.APPROVED)

    def get_participation_ratio(self, user):
        """
        Ratio between "given votes" / "possible votes" for an specific user.
        """
        max_votes = (
            self.comments
                .filter(status=Comment.APPROVED)
                .exclude(author=user)
                .count()
        )
        if not max_votes:
            return 0
        else:
            votes = (
                Vote.objects
                    .filter(comment__conversation_id=self.id, author=user)
                    .count()
            )
            return votes / max_votes

    def get_next_comment(self, user, default=NOT_GIVEN):
        """
        Returns a random comment that user didn't vote yet.

        If default value is not given, raises a Comment.DoesNotExit exception
        if no comments are available for user.
        """
        unvoted_comments = self.comments.filter(
            ~Q(author_id=user.id),
            ~Q(votes__author_id=user.id),
            status=Comment.STATUS.APPROVED,
        )
        size = unvoted_comments.count()
        if size:
            return unvoted_comments[randrange(0, size)]
        elif default is not NOT_GIVEN:
            return default
        else:
            msg = _('No comments available for this user')
            raise Comment.DoesNotExist(msg)

    def get_limit_status(self, user):
        """
        Verify specific user nudge status in a conversation
        """
        limits = self.limits or Limits()
        return limits.get_comment_status(user, self)

    def get_vote_data(self, user=None):
        """
        Like get_votes(), but resturn a list of (value, author, comment)
        tuples for each vote cast in the conversation.
        """
        return list(self.get_votes(user))


def vote_count(conversation, type=None):
    """
    Return the number of votes of a given type

    ``type=None`` for all votes.
    """

    kwargs = {'value': type} if type is not None else {}
    return (
        Vote.objects
            .filter(comment__conversation_id=conversation.id, **kwargs)
            .count()
    )


def comment_count(conversation, type=None):
    """
    Return the number of comments of a given type.

    ``type=None`` for all comments.
    """

    kwargs = {'status': type} if type is not None else {}
    return conversation.comments.filter(**kwargs).count()
