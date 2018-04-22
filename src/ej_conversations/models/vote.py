from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

VOTING_ERROR = (lambda value: ValueError(
    f"vote should be one of 'agree', 'disagree' or 'skip', got {value}")
)


class Vote(models.Model):
    """
    A single vote cast for a comment.
    """
    # Be aware this is the opposite of polis. Eg. in polis, agree is -1.
    AGREE = 1
    SKIP = 0
    DISAGREE = -1

    VOTE_CHOICES = (
        (AGREE, _('Agree')),
        (SKIP, _('Skip')),
        (DISAGREE, _('Disagree')),
    )
    VOTE_NAMES = {
        AGREE: 'agree',
        DISAGREE: 'disagree',
        SKIP: 'skip',
    }
    VOTE_VALUES = {v: k for k, v in VOTE_NAMES.items()}

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='votes',
        on_delete=models.PROTECT,
    )
    comment = models.ForeignKey(
        'Comment',
        related_name='votes',
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
    )
    value = models.IntegerField(
        _('Vote value'),
        choices=VOTE_CHOICES,
        help_text=_(
            'Numeric values: (disagree: -1, skip: 0, agree: 1)'
        ),
    )

    class Meta:
        unique_together = ('author', 'comment')

    @classmethod
    def normalize_vote(cls, value):
        """
        Normalize numeric and string values to the correct vote value that
        should be stored in the database.
        """
        if value in cls.VOTE_NAMES:
            return value
        try:
            return cls.VOTE_VALUES[value]
        except KeyError:
            raise VOTING_ERROR(value)

    def clean(self, *args, **kwargs):
        if self.comment.is_pending:
            msg = _('non-moderated comments cannot receive votes')
            raise ValidationError(msg)
