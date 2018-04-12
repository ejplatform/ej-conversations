from django.apps import AppConfig
from django.conf import settings


class EjConversationsConfig(AppConfig):
    name = 'ej_conversations'
    verbose_name = "EJ Conversations"

    def ready(self):
        if getattr(settings, 'EJ_CONVERSATIONS_ACTSTREAM', False):
            from actstream import registry

            registry.register(self.get_model('Conversation'))
            registry.register(self.get_model('Comment'))
            registry.register(self.get_model('Vote'))
