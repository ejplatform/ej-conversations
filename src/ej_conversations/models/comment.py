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
    is_approved = property(lambda self: self.status == self.STATUS.APPROVED)

    class Meta:
        unique_together = ('conversation', 'content')

    def __str__(self):
        return self.content

    def vote(self, author, value, commit=True):
        """
        Cast a vote for the current comment.
        """
        log.debug(f'Vote: {author} - {value}')
        vote = Vote(author=author, comment=self, value=value)
        vote.full_clean()
        if commit:
            vote.save()
        return vote

    def get_statistics(self):
        """
        Return full voting statistics for given comment.
        """

        return dict(
            agree=votes_counter(self, Vote.AGREE),
            disagree=votes_counter(self, Vote.DISAGREE),
            skip=votes_counter(self, Vote.SKIP),
            total=votes_counter(self),
        )


def votes_counter(comment, value=None):
    if value is None:
        return comment.votes.filter(value=value).count()
    else:
        return comment.votes.count()
