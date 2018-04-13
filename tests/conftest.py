import pytest
from ej_conversations.mommy_recipes import  *


class ApiClient:
    def __init__(self, client):
        self.client = client

    def get(self, url, raw=False):
        response = self.client.get(url)
        return response if raw else response.data


@pytest.fixture
def api(client):
    return ApiClient(client)