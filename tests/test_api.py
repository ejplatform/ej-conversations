class TestRoutes:
    def test_categories_endpoint(self, category_db, api):
        assert api.get('/categories/category/') == {
            'links': {'self': 'http://testserver/categories/category/'},
            'name': 'Category',
            'slug': 'category',
            'image': None,
            'image_caption': '',
        }
        assert api.get('/categories/bad-category/', raw=True).status_code == 404

    def test_users_endpoint(self, user_db, root_db, api):
        assert api.get('/users/root/') == {
            'url': 'http://testserver/users/root/',
            'username': 'root',
        }
        assert api.get('/users/user/') == {
            'url': 'http://testserver/users/user/',
            'username': 'user',
        }

    def test_conversations_endpoint(self, conversation_db, api):
        data = api.get('/conversations/conversation/', exclude=['created', 'modified'])
        assert data == {
            'links': {
                'approved_comments': 'http://testserver/conversations/conversation/approved_comments',
                'author': 'http://testserver/users/user/',
                'random_comment': 'http://testserver/conversations/conversation/random_comment',
                'self': 'http://testserver/conversations/conversation/',
                'user_data': 'http://testserver/conversations/conversation/user_data',
                'votes': 'http://testserver/conversations/conversation/votes',
            },
            'author_name': 'user',
            'category': None,
            'title': 'Conversation',
            'slug': 'conversation',
            'description': 'description',
            'is_promoted': False,
            'statistics': {
                'comments': {
                    'approved': 0,
                    'rejected': 0,
                    'pending': 0,
                    'total': 0,
                },
                'votes': {
                    'agree': 0,
                    'disagree': 0,
                    'skip': 0,
                    'total': 0,
                },
                'participants': 0,
            },
        }

        # Random conversations
        assert api.get('/conversations/random/', raw=True).status_code == 200
