import pytest

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.accounts.test.factories import UserFactory
from api.supply_chain_update.models import StrategicActionUpdate
from api.supply_chain_update.test.factories import StrategicActionUpdateFactory


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


@pytest.fixture
def test_in_progress_strategic_action_update():
    update = StrategicActionUpdateFactory()
    update.save()
    yield update


@pytest.fixture
def test_completed_strategic_action_update():
    update = StrategicActionUpdateFactory(status=StrategicActionUpdate.Status.COMPLETED)
    update.save()
    yield update


@pytest.fixture
def test_submitted_strategic_action_update():
    update = StrategicActionUpdateFactory(status=StrategicActionUpdate.Status.SUBMITTED)
    update.save()
    yield update
