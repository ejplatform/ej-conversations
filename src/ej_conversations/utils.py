from enum import Enum

from autoslug.settings import slugify as default_slugify
from django.utils.translation import ugettext_lazy as _


def custom_slugify(value):
    return default_slugify(value).lower()


class CommentLimitStatus(Enum):
    """
    Track the nudge status of a user in a conversation.
    """
    OK = 'ok'
    ALERT = 'alert'
    TEMPORARILY_BLOCKED = 'temporarily_blocked'
    BLOCKED = 'blocked'


CommentLimitStatus.MESSAGES = {
    CommentLimitStatus.OK: {
        'state': 'normal',
        'message': _('You can still post comments'),
        'status_code': 201,  # HTTP OK
        'error': False,
    },
    CommentLimitStatus.ALERT: {
        'state': 'alert',
        'message': _('Please, be careful posting too many comments'),
        'status_code': 201,  # HTTP OK
        'error': False,
    },
    CommentLimitStatus.BLOCKED: {
        'state': 'blocked',
        'message': _('Sorry, you cannot post more comments in this conversation'),
        'status_code': 429,  # HTTP too many requests
        'error': True,
    },
    CommentLimitStatus.TEMPORARILY_BLOCKED: {
        'state': 'temporarily_blocked',
        'message': _('Sorry, you are temporarily blocked. Please wait to be able to post again'),
        'status_code': 429,  # HTTP too many requests
        'error': True,
    },
}
