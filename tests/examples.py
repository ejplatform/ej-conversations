CATEGORY = {'links': {'self': 'http://testserver/categories/category/'}, 'name': 'Category', 'slug': 'category',
    'image': None, 'image_caption': '', }
USER_ROOT = {'url': 'http://testserver/users/root/', 'username': 'root', }
USER = {'url': 'http://testserver/users/user/', 'username': 'user', }
COMMENT = {'author_name': 'author', 'content': 'comment', 'id': 1,
               'links': {'self': 'http://testserver/comments/1/', 'author': 'http://testserver/users/author/',
                         'conversation': 'http://testserver/conversations/conversation/',
                         'vote': 'http://testserver/comments/1/vote', }, 'rejection_reason': '',
               'statistics': {'agree': 0, 'disagree': 0, 'missing': 0, 'skip': 0, 'total': 0, },
               'status': 'APPROVED', }
CONVERSATION = {'links': {'self': 'http://testserver/conversations/conversation/',
                  'approved_comments': 'http://testserver/conversations/conversation/approved_comments',
                  'author': 'http://testserver/users/user/',
                  'category': 'http://testserver/categories/category/',
                  'random_comment': 'http://testserver/conversations/conversation/random_comment',
                  'user_data': 'http://testserver/conversations/conversation/user_data',
                  'votes': 'http://testserver/conversations/conversation/votes', },
        'author_name': 'user', 'category_name': 'Category', 'title': 'Conversation',
        'slug': 'conversation', 'question': 'question?', 'is_promoted': False,
        'statistics': {'comments': {'approved': 0, 'rejected': 0, 'pending': 0, 'total': 0, },
                       'votes': {'agree': 0, 'disagree': 0, 'skip': 0, 'total': 0, },
                       'participants': 0, }, }
VOTE = {'links': {'comment': 'http://testserver/comments/1/', 'self': 'http://testserver/votes/1/', },
        'action': 'agree', 'comment_text': 'comment', }