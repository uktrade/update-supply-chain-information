import pytest

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.accounts.test.factories import UserFactory


@pytest.fixture
def test_user():
    user = UserFactory(first_name="Test")
    user.save()
    yield user


@pytest.fixture
def test_client_with_token(test_user):
    user = test_user
    Token.objects.create(user=user)
    token = Token.objects.get(user__id=user.id)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    yield client
