import pytest

from ej_conversations.models import (
    Conversation,
    Comment,
    Vote,
)
from .helpers import (
    create_valid_comment,
    create_valid_comments,
)

pytestmark = pytest.mark.django_db


class TestConversation:

    def test_get_random_comment(self, user, other_user, conversation: Conversation):
        """
        Should return a conversation's comment
        """
        comments = create_valid_comments(3, conversation, user)
        random_comment = conversation.get_next_comment(other_user)

        assert random_comment in comments

    def test_get_random_comment_should_return_only_approved_comments(self, user,
                                                                     other_user, conversation: Conversation):
        """
        Should not return rejected or unmoderated comments
        """
        comments = [create_valid_comment(conversation, user, approval)
                    for approval in [Comment.REJECTED, Comment.PENDING]]

        with pytest.raises(Comment.DoesNotExist) as err:
            conversation.get_next_comment(other_user)

    def test_get_random_comment_should_return_only_unvoted_comments(self, user,
                                                                    other_user, conversation: Conversation):
        """
        Should not return any comment because the only one is already voted
        """
        comment = create_valid_comment(conversation, user)
        comment.votes.create(author=other_user, value=Vote.AGREE)

        with pytest.raises(Comment.DoesNotExist) as err:
            conversation.get_next_comment(other_user)

    def test_random_comment_should_not_be_of_current_user(self, user, conversation: Conversation):
        """
        User can't get its own comment
        """
        create_valid_comment(conversation, user)

        with pytest.raises(Comment.DoesNotExist) as err:
            conversation.get_next_comment(user)
