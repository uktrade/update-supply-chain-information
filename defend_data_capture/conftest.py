import pytest

from django.test import Client
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import User
from accounts.test.factories import UserFactory
from supply_chains.models import StrategicActionUpdate
from supply_chains.test.factories import StrategicActionUpdateFactory


@pytest.fixture
def logged_in_client(test_user):
    client = Client()
    client.force_login(test_user)
    yield client


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
