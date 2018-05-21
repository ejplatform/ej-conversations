from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ..utils import CommentLimitStatus


class Limits(models.Model):
    """
    Configure the allowed rate users can post and vote on comments.
    """

    name = models.CharField(
        _('Name'),
        max_length=140,
        unique=True,
        help_text=_(
            'A memorable description of your limit configuration. The '
            'description is used to reference this configuration in other '
            'conversation objects.'
        ),
    )
    interval = models.IntegerField(
        _('Reference interval (in seconds)'),
        default=10 * 60,
        help_text=_(
            'We avoid spam and bots by preventing users for posting too many '
            'comments or votes in the given interval.'
        ),
    )
    max_comments_in_interval = models.IntegerField(
        _('Maximum number of comments'),
        default=1,
        help_text=_(
            'Users can post at most this number of comments in the reference '
            'interval.'
        ),
    )
    max_comments_per_conversation = models.IntegerField(
        _('Maximum number of comments (global)'),
        default=2,
        help_text=_(
            'Limit the number of comments in a single conversation.'
        ),
    )
    max_votes_in_interval = models.IntegerField(
        _('Maximum number of votes'),
        default=100,
        help_text=_(
            'Limit the number of votes. Usually this should be a much higher '
            'number than the number of comments limit.'
        ),
    )
    max_votes_per_conversation = models.IntegerField(
        _('Maximum number of votes (global)'),
        blank=True, null=True,
        help_text=_(
            'Limit the number of votes in a single conversation. No limit is'
            'enforced by default.'
        ),
    )
    timedelta = property(lambda self: timezone.timedelta(seconds=self.interval))

    class Meta:
        verbose_name_plural = _('Usage limits')

    def __str__(self):
        return self.name

    def user_status(self, user, conversation):
        """
        Verify the limits applied to a user in a conversation.
        """

        n_total = self.remaining_comments(user, conversation)
        if n_total == 0:
            return CommentLimitStatus.BLOCKED

        n_interval = self.remaining_comments(user, conversation, interval=True)
        if n_interval == 0:
            return CommentLimitStatus.TEMPORARILY_BLOCKED
        elif n_interval == 1 or n_total == 1:
            return CommentLimitStatus.ALERT
        else:
            return CommentLimitStatus.OK

    def remaining_comments(self, user, conversation, interval=False):
        """
        Return the number of comments a user can still post in a conversation.

        If interval=True, compute only comments still allowed in the reference
        interval rather than the global comment limit.
        """
        if interval:
            start_time = self._now() - self.timedelta
            filter = dict(conversation_id=conversation.id, created__gte=start_time)
            comments = user.comments.filter(**filter).count()
            return max(self.max_comments_in_interval - comments, 0)
        else:
            filter = dict(conversation_id=conversation.id)
            comments = user.comments.filter(**filter).count()
            return max(self.max_comments_per_conversation - comments, 0)

    @staticmethod
    def _now():
        # Useful for mocking
        return timezone.now()
