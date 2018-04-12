from logging import getLogger

from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel, StatusModel

from .vote import Vote

log = getLogger('ej-conversations')


class Comment(StatusModel, TimeStampedModel):
    """
    A comment on a conversation.
    """

    STATUS = Choices(
        ('PENDING', _('awaiting moderation')),
        ('APPROVED', _('approved')),
        ('REJECTED', _('rejected')),
    )

    conversation = models.ForeignKey(
        'Conversation',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    content = models.TextField(
        _('Content'),
        blank=False,
        validators=[MaxLengthValidator(140)],
    )
    rejection_reason = models.TextField(
        _('Rejection reason'),
        blank=True,
    )

    class Meta:
        unique_together = ('conversation', 'content')

    def __str__(self):
        return self.content

    agree_votes_no = property(lambda self: votes_counter(self, Vote.AGREE))
    disagree_votes_no = property(lambda self: votes_counter(self, Vote.DISAGREE))
    pass_votes_no = property(lambda self: votes_counter(self, Vote.SKIP))
    total_votes_no = property(lambda self: votes_counter(self))

    def vote(self, user, vote, commit=True):
        """
        Cast a user vote for the current comment.
        """

        log.debug(f'Vote: {user} - {vote}')
        make_vote = Vote.objects.create if commit else Vote
        return make_vote(author=user, comment=self, value=vote)


def votes_counter(self, value=None):
    if value is None:
        return self.votes.filter(value=value).count()
    else:
        return self.votes.count()
