from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ..utils import CommentLimitStatus


class Limits(models.Model):
    """
    Configure the allowed rate users can post and vote on comments.
    """

    description = models.CharField(
        _('Description'),
        max_length=140,
    )
    interval = models.IntegerField(
        _('Reference interval'),
        default=10 * 60,
        help_text=_('Inteval in seconds'),
    )
    max_comments_in_interval = models.IntegerField(
        _('Maximum number of posts in an interval'),
        default=3,
        help_text=_('Maximum number of comments in the reference interval'),
    )
    max_votes_in_interval = models.IntegerField(
        _('Maximum number of votes in the given interval'),
        default=100,
        help_text=_('Maximum number of votes in the reference interval'),
    )
    max_comments_per_conversation = models.IntegerField(
        _('Maximum number of posts'),
        default=5,
        help_text=_('Global number of comments'),
    )

    class Meta:
        verbose_name_plural = _('Usage limits')

    def __str__(self):
        return self.description

    def get_comment_status(self, user, conversation):
        """
        Verify specific user nudge status in a conversation
        """
        n_total = self.remaining_comments(user, conversation)
        if n_total == 0:
            return CommentLimitStatus.BLOCKED

        n_interval = self.remaining_interval_comments(user, conversation)
        if n_interval == 0:
            return CommentLimitStatus.TEMPORARILY_BLOCKED
        elif n_interval == 1 or n_total == 1:
            return CommentLimitStatus.ALERT
        else:
            return CommentLimitStatus.OK

    def remaining_comments(self, user, conversation):
        """
        Return the number of comments a user can still post in a conversation.
        """
        comments = user.comments.filter(conversation_id=conversation.id).count()
        return max(self.max_comments_per_conversation - comments, 0)

    def remaining_interval_comments(self, user, conversation):
        """
        Return the number of comments a user can still post in a conversation
        in the reference interval.
        """
        start_time = timezone.now() - timezone.timedelta(seconds=self.interval)
        comments = (
            user.comments
                .filter(conversation_id=conversation.id)
                .filter(created__gte=start_time)
                .count()
        )
        return max(self.max_comments_in_interval - comments)
