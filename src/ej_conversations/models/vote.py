from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


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

    def clean(self, *args, **kwargs):
        if not self.comment.is_approved:
            msg = _('comment must be approved to receive votes')
            raise ValidationError(msg)
