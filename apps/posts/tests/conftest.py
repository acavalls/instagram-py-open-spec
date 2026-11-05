import pytest
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_api_client(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user
