from logging import getLogger

from django.conf import settings
from django.core.exceptions import ValidationError
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
    STATUS_MAP = {
        'pending': STATUS.PENDING, 'approved': STATUS.APPROVED,
        'rejected': STATUS.REJECTED,
    }
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
        max_length=140,
        help_text=_('Body of text for the comment'),
    )
    rejection_reason = models.TextField(
        _('Rejection reason'),
        blank=True,
        help_text=_(
            'You must provide a reason to reject a comment. Users will receive '
            'this feedback.'
        ),
    )
    is_approved = property(lambda self: self.status == self.STATUS.APPROVED)
    is_pending = property(lambda self: self.status == self.STATUS.PENDING)
    is_rejected = property(lambda self: self.status == self.STATUS.REJECTED)

    @classmethod
    def normalize_status(cls, value):
        """
        Convert status string values to safe db representations.
        """
        if value is None:
            return cls.STATUS.PENDING
        try:
            return cls.STATUS_MAP[value]
        except KeyError:
            raise ValueError(f'invalid status value: {value}')

    class Meta:
        unique_together = ('conversation', 'content')

    def __str__(self):
        return self.content

    def clean(self):
        super().clean()
        if self.status == self.STATUS.REJECTED and not self.rejection_reason:
            msg = _('Must give a reason to reject a comment')
            raise ValidationError({'rejection_reason': msg})

    def vote(self, author, value, commit=True):
        """
        Cast a vote for the current comment. Vote must be one of 'agree', 'skip'
        or 'disagree'.

        >>> comment.vote(request.user, 'agree')                 # doctest: +SKIP
        """
        value = Vote.normalize_vote(value)
        log.debug(f'Vote: {author} - {value}')
        vote = Vote(author=author, comment=self, value=value)
        vote.full_clean()
        if commit:
            vote.save()
        return vote

    def get_statistics(self, ratios=False):
        """
        Return full voting statistics for comment.

        Args:
            ratios (bool):
                If True, also include 'agree_ratio', 'disagree_ratio', etc
                fields each original value. Ratios count the percentage of
                votes in each category.

        >>> comment.get_statistics()                            # doctest: +SKIP
        {
            'agree': 42,
            'disagree': 10,
            'skip': 25,
            'total': 67,
            'missing': 102,
        }
        """

        agree = votes_counter(self, Vote.AGREE)
        disagree = votes_counter(self, Vote.DISAGREE)
        skip = votes_counter(self, Vote.SKIP)
        total = agree + disagree + skip

        missing = Vote.objects.values_list('author_id').distinct().count() - total
        stats = dict(agree=agree, disagree=disagree, skip=skip,
                     total=total, missing=missing)

        if ratios:
            e = 1e-50  # prevents ZeroDivisionErrors
            stats.update(
                agree_ratio=agree / (total + e),
                disagree_ratio=disagree / (total + e),
                skip_ratio=skip / (total + e),
                missing_ratio=missing / (missing + total + e),
            )
        return stats


def votes_counter(comment, value=None):
    if value is not None:
        return comment.votes.filter(value=value).count()
    else:
        return comment.votes.count()
