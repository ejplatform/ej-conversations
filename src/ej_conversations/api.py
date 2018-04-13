from . import viewsets


def register_routes(router, register_user=False):
    register = router.register
    register(r'categories', viewsets.CategoryViewSet, base_name='category')
    register(r'conversations', viewsets.ConversationViewSet, base_name='conversation')
    register(r'comments', viewsets.CommentViewSet, base_name='comment')
    register(r'votes', viewsets.VoteViewSet, base_name='vote')

    if register_user:
        register(r'users', viewsets.UserViewSet, base_name='user')
    return router
