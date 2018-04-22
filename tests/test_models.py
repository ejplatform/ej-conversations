import pytest
from django.core.exceptions import ValidationError

from ej_conversations.models import Vote


class TestCategory:
    def test_category_unhappy_paths(self, category):
        # Has image caption, but no image
        with pytest.raises(ValidationError):
            category.image_caption = 'some caption'
            category.clean()

    def test_create_conversation(self, category, user):
        conversation = category.create_conversation('what?', 'test', user,
                                                    commit=False)
        assert conversation.category is category


class TestVote:
    def test_unique_vote_per_comment(self, mk_user, comment_db):
        user = mk_user()
        comment_db.vote(user, 'agree')
        with pytest.raises(ValidationError):
            comment_db.vote(user, 'disagree')

    def test_cannot_vote_in_non_moderated_comment(self, comment_db, user_db):
        comment_db.status = comment_db.STATUS.PENDING

        with pytest.raises(ValidationError):
            comment_db.vote(user_db, 'agree')

    def test_vote_unhappy_paths(self, comment_db, user_db):
        with pytest.raises(ValueError):
            comment_db.vote(user_db, 42)

    def test_vote_happy_paths(self, comment_db, mk_user):
        vote1 = comment_db.vote(mk_user(username='user1'), 'agree')
        vote2 = comment_db.vote(mk_user(username='user2'), Vote.AGREE)
        assert vote1.value == vote2.value
