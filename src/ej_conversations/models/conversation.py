import logging
from random import randrange

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .comment import Comment
from .limits import Limits
from .managers import ConversationManager
from .vote import Vote
from ..utils import CommentLimitStatus
from ..utils import custom_slugify

NOT_GIVEN = object()

BAD_LIMIT_STATUS = {CommentLimitStatus.BLOCKED,
                    CommentLimitStatus.TEMPORARILY_BLOCKED}
log = logging.getLogger('ej_conversations')


class Conversation(TimeStampedModel):
    """
    A topic of conversation.
    """

    question = models.TextField(
        _('Question'),
        help_text=_(
            'A question that is displayed to the users in a conversation card. (e.g.: How can we '
            'improve the school system in our community?)'
        ),
    )
    title = models.CharField(
        _('Title'),
        max_length=255,
        help_text=_(
            'A short description about this conversations. This is used for internal reference'
            'and to create URL slugs. (e.g. School system)'
        )
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
        help_text=_(
            'Only the author and administrative staff can edit this conversation.'
        )
    )
    category = models.ForeignKey(
        'Category',
        related_name='conversations',
        on_delete=models.CASCADE,
    )
    slug = AutoSlugField(
        unique=True,
        populate_from='title',
        slugify=custom_slugify,
    )
    is_promoted = models.BooleanField(
        _('Promoted'),
        default=False,
        help_text=_(
            'Promoted conversations take priority in the list of conversations.'
        )
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

    category_name = property(lambda self: self.category.name)
    objects = ConversationManager()
    votes = property(lambda self:
                     Vote.objects.filter(comment__conversation_id=self.id))

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title

    @property
    def approved_comments(self):
        """
        Return a sequence of all approved comments for conversation.
        """
        return self.comments.filter(status=Comment.STATUS.APPROVED)

    def get_votes(self, user=None):
        """
        Get all votes for the conversation.

        If a user is supplied, filter votes for the given user.
        """
        kwargs = {'author_id': user.id} if user else {}
        return Vote.objects.filter(comment__conversation_id=self.id, **kwargs)

    def get_absolute_url(self):
        map = getattr(settings, 'EJ_CONVERSATIONS_URLMAP', {})
        fmt = map.get('conversation-detail', None)
        if fmt is None:
            return reverse('conversation-detail', kwargs={'slug': self.slug})
        return fmt.format(conversation=self)

    def create_comment(self, author, content, commit=True, *, status=None,
                       check_limits=True, **kwargs):
        """
        Create a new comment object for the given user.

        If commit=True (default), comment is persisted on the database.

        By default, this method check if the user can post according to the
        limits imposed by the conversation. It also normalizes duplicate
        comments and reuse duplicates from the database.
        """

        # Convert status, if necessary
        status = Comment.normalize_status(status)
        kwargs['status'] = status

        # Check limits
        if check_limits:
            limit = self.get_limit_status(author)
            if limit in BAD_LIMIT_STATUS:
                raise PermissionError(CommentLimitStatus.MESSAGES[limit])

        make_comment = Comment.objects.create if commit else Comment
        kwargs.update(author=author, content=content)
        comment = make_comment(conversation=self, **kwargs)
        log.info('new comment: %s' % comment)
        return comment

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

    def get_user_statistics(self, user):
        """
        Get information about user.
        """
        max_votes = self.get_maximum_votes(user)
        given_votes = self.get_given_votes(user)

        e = 1e-50  # for numerical stability
        return dict(
            votes=given_votes,
            missing_votes=max_votes - given_votes,
            participation_ratio=given_votes / (max_votes + e),
        )

    def get_maximum_votes(self, user):
        """
        Return the maximum number of votes a user can cast in the given
        conversation.
        """
        return (
            self.comments
                .filter(status=Comment.STATUS.APPROVED)
                .exclude(author_id=user.id)
                .count()
        )

    def get_given_votes(self, user):
        """
        Get the number of votes a given user has cast in conversation.
        """
        if user.id is None:
            return 0
        return (
            Vote.objects
                .filter(comment__conversation_id=self.id, author=user)
                .count()
        )

    def get_next_comment(self, user, default=NOT_GIVEN):
        """
        Returns a random comment that user didn't vote yet.

        If default value is not given, raises a Comment.DoesNotExit exception
        if no comments are available for user.
        """
        unvoted_comments = self.approved_comments.filter(
            ~Q(author_id=user.id),
            ~Q(votes__author_id=user.id),
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
        Verify specific user limits for posting comments in a conversation.
        """
        limits = self.limits or Limits()
        return limits.get_comment_status(user, self)

    def get_vote_data(self, user=None):
        """
        Like get_votes(), but restur a list of (value, author, comment)
        tuples for each vote cast in the conversation.
        """
        return list(self.get_votes(user))

    def set_limits(self, limits=None, commit=True, **kwargs):
        """
        Sets the limit object for conversation.

        It accepts a simple :cls:`Limits` object, its name as a string or a
        set of keyword arguments defining the limit fields.
        """
        if isinstance(limits, str):
            limits = Limits.objects.get(name=limits)
        if not isinstance(limits, Limits):
            limits = Limits(**kwargs)
        elif kwargs:
            print(limits)
            limits.__init__(**kwargs)
            print(limits)
        if not limits.name:
            limits.name = f'{self.slug} limits'

        self.limits = limits
        if commit:
            limits.save()
        if commit:
            self.save(update_fields=['limits'])
        return limits


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
