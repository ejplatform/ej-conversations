from tests.examples import CATEGORY, USER_ROOT, USER, COMMENT, CONVERSATION, VOTE


class TestRoutes:
    def test_categories_endpoint(self, category_db, api):
        assert api.get('/categories/category/') == CATEGORY
        assert api.get('/categories/bad-category/', raw=True).status_code == 404

    def test_users_endpoint(self, user_db, root_db, api):
        assert api.get('/users/root/') == USER_ROOT
        assert api.get('/users/user/') == USER

    def test_conversations_endpoint(self, conversation_db, api):
        path = f'/conversations/{conversation_db.slug}/'
        data = api.get(path,
                       exclude=['created', 'modified'])
        assert data == CONVERSATION

        # Random conversations
        assert api.get('/conversations/random/', raw=True).status_code == 200

        # Check inner links work
        assert api.get(path + 'user_data/') == {
            'missing_votes': 0, 'participation_ratio': 0.0, 'votes': 0
        }
        assert api.get(path + 'votes/') == []
        assert api.get(path + 'approved_comments/') == []
        assert api.get(path + 'random_comment/') == {
            'error': True,
            'message': 'No comments available for this user',
        }

    def test_comments_endpoint(self, comment_db, api):
        data = api.get(f'/comments/{comment_db.id}/',
                       exclude=['created', 'modified'])
        assert data == COMMENT

    def test_votes_endpoint(self, vote_db, api):
        # Requesting from non-authenticated user
        assert api.get('/votes/') == {
            'count': 0, 'next': None, 'previous': None, 'results': [],
        }

        # Now we force authentication
        api.client.force_login(vote_db.author, backend=None)
        assert api.get(f'/votes/{vote_db.id}/') == VOTE
