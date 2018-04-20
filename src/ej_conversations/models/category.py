from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from ..fields import AutoSlugField
from ..utils import custom_slugify


class Category(TimeStampedModel):
    """
    Base category that a conversation belongs to.

    Declares category name and stores some metadata.
    """

    name = models.CharField(
        _('Name'),
        max_length=255,
        unique=True,
        help_text=_('Unique category name. Hint: list of categories is public.'),
    )
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
        slugify=custom_slugify,
    )
    image = models.ImageField(
        _('Image'),
        upload_to='conversations/categories',
        null=True, blank=True,
    )
    image_caption = models.CharField(
        _('Image caption'),
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def new_conversation(self, question, title, author, *, commit=True, **kwargs):
        """
        Creates a new conversation in the current category.
        """
        kwargs.update(title=title, question=question, author=author)
        if commit:
            return self.conversations.create(**kwargs)
        else:
            from .conversation import Conversation

            return Conversation(category=self, **kwargs)
