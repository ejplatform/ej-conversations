import pytest
from django.contrib.auth.models import User
from model_mommy.recipe import Recipe

from .models import Comment, Conversation, Category

user = Recipe(User, is_superuser=False, username='user')
root = Recipe(User, is_superuser=True, username='root')
category = Recipe(Category, name='Category', slug='category')
comment = Recipe(Comment)
conversation = Recipe(
    Conversation,
    title='Conversation',
    slug='conversation',
    author=user.make,
    description='description'
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

    globals()['fixture_' + name] = fixture_function
    globals()['fixture_' + name + '_db'] = fixture_function_db
    globals()['fixture_' + name + '_rec'] = fixture_function_rec
    globals()['fixture_' + name + '_mk'] = fixture_function_mk


[make_fixture(v, k)
 for k, v in list(globals().items())
 if isinstance(v, Recipe)]
