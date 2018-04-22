"""
Those scenarios are difficult to test using unit tests.

We describe simple stories with lots of asserts in the middle. This document
some common usage scenarios of the API and can protect us from bad
refactorings.
"""
import datetime
import pytest
import mock
from types import SimpleNamespace
import random

from contextlib import contextmanager
from django.core.exceptions import ValidationError

from ej_conversations.models import Vote, Limits


class TestCommentLimitsStory:
    """
    Application prevents user from posting too many comments in too little
    time.
    """

    @contextmanager
    def time_control(self):
        self.delay_secs = 0
        self.real_time = Limits._now

        def sleep(time):
            self.delay_secs += time

        with mock.patch.object(Limits, '_now', self.now):
            yield SimpleNamespace(sleep=sleep)

    def now(self):
        delta = datetime.timedelta(seconds=self.delay_secs)
        return self.real_time() + delta

    def test_comment_limits_are_enforced(self, mk_conversation, mk_user):
        with self.time_control() as time:
            # We create a basic conversation and a user.
            conversation = mk_conversation()
            user = mk_user(username='test')

            # Lets set some conservative limits...
            conversation.set_limits(
                interval=10,
                max_comments_in_interval=2,
                max_comments_per_conversation=4,
                max_votes_in_interval=2,
                max_votes_per_conversation=4,
            )

            # User can post two comments without problems.
            conversation.create_comment(user, 'cmt1')
            conversation.create_comment(user, 'cmt2')

            # It will have problem in comment #3.
            with pytest.raises(PermissionError):
                conversation.create_comment(user, 'cmt3')

            # We mock global time, now everything should be ok :)
            time.sleep(11)
            conversation.create_comment(user, 'cmt4-bad')
            assert user.comments.count() == 3

            # User keeps posting.
            conversation.create_comment(user, 'cmt4')

            # But has reached global limit.
            with pytest.raises(PermissionError):
                conversation.create_comment(user, 'cmt5-bad')

            # Never again...
            with pytest.raises(PermissionError):
                conversation.create_comment(user, 'cmt5-bad-again')


class TestStatistics:
    """
    We create a small, but plausible scenario of comments in a conversation
    and check if statistics are correct.
    """

    def test_conversation_statistics(self, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user()

        # Three groups of people with different preferences
        g1 = [mk_user(username=f'user_a{i}') for i in range(3)]
        g2 = [mk_user(username=f'user_b{i}') for i in range(3)]
        g3 = [mk_user(username=f'user_c{i}') for i in range(2)]

        # User makes some comments
        comments = [
            conversation.create_comment(user, f'comment {i}',
                                        status='approved',
                                        check_limits=False)
            for i in range(5)
        ]

        # Now we vote...
        votes = []
        for i, comment in enumerate(comments):
            for user in g1:
                votes.append(comment.vote(user, 'agree'))
            for user in g2:
                votes.append(comment.vote(user, 'disagree'))

            # Alternate between a pair who skip and miss to a pair who miss
            # and then skip ==> 5 skips and 5 misses in total
            for j, user in enumerate(g3):
                if (i + j) % 2 == 0:
                    votes.append(comment.vote(user, 'skip'))

        # Now we check global statistics.
        stats = conversation.get_statistics()
        assert stats == {
            'comments': {
                'approved': 5,
                'pending': 0,
                'rejected': 0,
                'total': 5
            },
            'votes': {
                'agree': 15,
                'disagree': 15,
                'skip': 5,
                'total': 35,
            },
            'participants': 8,
        }

        # User can also check its own stats
        assert conversation.get_user_statistics(g1[0]) == {
            'missing_votes': 0,
            'participation_ratio': 1.0,
            'votes': 5,
        }
        assert conversation.get_user_statistics(g1[2]) == {
            'missing_votes': 0,
            'participation_ratio': 1.0,
            'votes': 5,
        }
        assert conversation.get_user_statistics(g3[0]) == {
            'missing_votes': 2,
            'participation_ratio': 3 / 5,
            'votes': 3,
        }
        assert conversation.get_user_statistics(g3[1]) == {
            'missing_votes': 3,
            'participation_ratio': 2 / 5,
            'votes': 2,
        }
