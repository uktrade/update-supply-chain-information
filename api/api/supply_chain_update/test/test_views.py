import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from api.supply_chain_update.models import StrategicAction
from api.supply_chain_update.test.factories import (
    StrategicActionFactory,
    SupplyChainFactory,
)


@pytest.mark.django_db()
def test_fails_if_unauthenticated():
    """
    Test that a 401 is returned if a request is made to the
    '/strategic-action' endpoint from an unauthenticated user.
    """
    url = reverse("strategic-action-list")
    client = APIClient()
    response = client.get(
        url,
    )
    assert response.status_code == 401


@pytest.mark.django_db()
def test_get_all_strategic_actions(
    test_client_with_token,
):
    """
    Test that all strategic action objects are returned when an
    authorised request is made to the '/strategic-action' endpoint.
    """
    strat_act = StrategicActionFactory()
    num_actions = StrategicAction.objects.count()
    client = test_client_with_token
    url = reverse("strategic-action-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == num_actions
    assert response.data[0]["id"] == str(strat_act.id)


@pytest.mark.django_db()
def test_get_all_strategic_actions_from_a_given_supply_chain(
    test_client_with_token,
):
    """
    Test that when a supply chain id is given in query paramters,
    the '/strategic-action' endpoint returns a list of strategic actions
    related to that supply chain.
    """
    supply_chain = SupplyChainFactory()
    strategic_action = StrategicActionFactory(supply_chain=supply_chain)
    # Create additional strategic action not linked to this supply chain
    StrategicActionFactory()
    client = test_client_with_token
    response = client.get(
        "/strategic-actions/", {"supply_chain_id": supply_chain.id}
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(strategic_action.id)


@pytest.mark.django_db()
def test_all_strategic_actions_returned_if_query_param_empty(
    test_client_with_token,
):
    StrategicActionFactory()
    num_actions = StrategicAction.objects.count()
    client = test_client_with_token
    response = client.get("/strategic-actions/", {"supply_chain_id": ""})
    assert response.status_code == 200
    assert len(response.data) == num_actions
