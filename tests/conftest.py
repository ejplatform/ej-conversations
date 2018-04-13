from ej_conversations.mommy_recipes import *


class ApiClient:
    def __init__(self, client):
        self.client = client

    def _result(self, data, fields=None, exclude=()):
        if fields is not None:
            data = {k: v for k, v in data.items() if k in fields}
        for field in exclude:
            del data[field]
        return data

    def get(self, url, raw=False, **kwargs):
        response = self.client.get(url)
        data = response if raw else response.data
        return self._result(data, **kwargs)


@pytest.fixture
def api(client):
    return ApiClient(client)
