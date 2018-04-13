from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..validators import validate_color


class ConversationPhases(models.Model):
    """
    Data for other phases of the conversation.
    """

    conversation = models.OneToOneField(
        'Conversation',
        related_name='phases',
        on_delete=models.CASCADE,
    )
    dialog = models.TextField(
        _('Dialog'),
        blank=True,
    )
    response = models.TextField(
        _('Response'),
        blank=True,
    )
    position = models.IntegerField(
        _('Position'),
        default=0,
    )
    opinion = models.TextField(
        _('Our Opinion'),
        blank=True,
    )


class ConversationStyle(models.Model):
    description = models.CharField(
        _('Description'),
        max_length=140,
    )
    background_image = models.ImageField(
        _('Background image'),
        upload_to='ej-conversations/backgrounds',
        null=True, blank=True,
    )
    background_color = models.CharField(
        _('Background color'),
        max_length=7,
        validators=[validate_color],
        null=True, blank=True,
    )
