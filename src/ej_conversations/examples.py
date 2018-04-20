"""
A few functions for creating plausible synthetic data.
"""
from django.contrib.auth import get_user_model
from random import choice

from django.db.models import Model

from .models import Category

User = get_user_model()


class ExampleData:
    def __init__(self, users, verbose):
        self.users = list(users)
        self.staff_users = [x for x in self.users if x.is_staff]
        self.verbose = verbose
        if verbose:
            self.log = (lambda x: 'Created: %s' % x)
        else:
            self.log = (lambda x: None)

    def __setattr__(self, key, value):
        if isinstance(value, Model):
            self.log(value)
        super().__setattr__(key, value)

    def make_categories(self):
        self.democracy, _ = Category.objects.get_or_create(name='Democracy')
        self.tech, _ = Category.objects.get_or_create(name='Technical')

    def make_conversations(self):
        self.better_language = self.tech.new_conversation(
            'We want to create the best programming language. How it should be?',
            'A better programming language',
            self.get_staff_user(),
        )
        self.school_system = self.democracy.new_conversation(
            'How can we improve the school system in our community?',
            'School system',
            self.get_staff_user(),
        )

    def make_all(self):
        self.make_categories()
        self.make_conversations()

    def get_staff_user(self):
        return choice(self.staff_users)


def make_examples(users=None, verbose=False):
    """
    Takes a list of users and creates plausible synthetic data.
    """
    if users is None:
        users = User.objects.all()

    data = ExampleData(users, verbose)
    data.make_all()
