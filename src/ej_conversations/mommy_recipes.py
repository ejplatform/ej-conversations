import pytest
from django.contrib.auth import get_user_model
from model_mommy.recipe import Recipe

from .models import Comment, Conversation, Category, Vote

__all__ = ['user', 'root', 'category', 'conversation', 'comment', 'vote']

User = get_user_model()
user = Recipe(User, is_superuser=False, username='user')
root = Recipe(User, is_superuser=True, username='root', is_staff=True)
category = Recipe(Category, name='Category', slug='category')
conversation = Recipe(
    Conversation,
    title='Conversation',
    question='question?',
    slug='conversation',
    author=lambda: user.make(username='conversation_author'),
    category=category.make,
)
comment = Recipe(
    Comment,
    author=lambda: user.make(username='comment_author'),
    content='comment',
    conversation=conversation.make,
    status=Comment.STATUS.APPROVED,
)
vote = Recipe(
    Vote,
    comment=comment.make,
    author=lambda: user.make(username='voter'),
    value=Vote.AGREE,
)


def make_fixture(recipe, name):
    @pytest.fixture(name=name)
    def fixture_function():
        return recipe.prepare()

    @pytest.fixture(name=name + '_db')
    def fixture_function_db(db):
        return recipe.make()

    @pytest.fixture(name='rec_' + name)
    def fixture_function_rec():
        return recipe

    @pytest.fixture(name='mk_' + name)
    def fixture_function_mk(db):
        return recipe.make

    ns = {}
    ns['fixture_' + name] = fixture_function
    ns['fixture_' + name + '_db'] = fixture_function_db
    ns['fixture_' + name + '_rec'] = fixture_function_rec
    ns['fixture_' + name + '_mk'] = fixture_function_mk
    globals().update(ns)
    __all__.extend(ns)


[make_fixture(v, k)
 for k, v in list(globals().items())
 if isinstance(v, Recipe)]

del pytest
