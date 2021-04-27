import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from supply_chains.models import (
    StrategicAction,
    StrategicActionUpdate,
    SupplyChain,
)
from supply_chains.test.factories import (
    StrategicActionFactory,
    StrategicActionUpdateFactory,
    SupplyChainFactory,
)
from accounts.test.factories import GovDepartmentFactory


@pytest.mark.parametrize(
    "url_name",
    (
        "supply-chain-list",
        "strategic-action-list",
        "strategic-action-update-list",
    ),
)
def test_fails_if_unauthenticated(url_name):
    """
    Test that a 401 is returned if a request is made to the
     endpoints from an unauthenticated user.
    """
    url = reverse(url_name)
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
    Test that when a supply chain id is given in query parameters,
    the '/api/strategic-action' endpoint returns a list of strategic actions
    related to that supply chain.
    """
    supply_chain = SupplyChainFactory()
    strategic_action = StrategicActionFactory(supply_chain=supply_chain)
    # Create additional strategic action not linked to this supply chain
    StrategicActionFactory()
    client = test_client_with_token
    response = client.get(
        "/api/strategic-actions/", {"supply_chain_id": supply_chain.id}
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(strategic_action.id)


@pytest.mark.django_db()
def test_get_all_strategic_actions_that_are_archived(
    test_client_with_token,
):
    """
    Test that when is_archived is True in query parameters,
    the '/api/strategic-action' endpoint returns a list of strategic actions
    that are archived.
    """
    supply_chain = SupplyChainFactory()
    strategic_action = StrategicActionFactory(
        supply_chain=supply_chain, is_archived=True, archived_reason="A reason"
    )
    # Create additional strategic action not linked to this supply chain
    StrategicActionFactory()
    client = test_client_with_token
    response = client.get("/api/strategic-actions/", {"is_archived": True})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(strategic_action.id)


@pytest.mark.django_db()
def test_get_all_strategic_actions_that_are_not_archived(
    test_client_with_token,
):
    """
    Test that when is_archived is False in query parameters,
    the '/api/strategic-action' endpoint returns a list of strategic actions
    that are not archived.
    """
    supply_chain = SupplyChainFactory()
    strategic_action = StrategicActionFactory(
        supply_chain=supply_chain, is_archived=False
    )
    # Create archived strategic action
    StrategicActionFactory(is_archived=True, archived_reason="A reason")
    client = test_client_with_token
    response = client.get("/api/strategic-actions/", {"is_archived": False})
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
    response = client.get(
        "/api/strategic-actions/", {"supply_chain_id": "", "is_archived": ""}
    )
    assert response.status_code == 200
    assert len(response.data) == num_actions


@pytest.mark.django_db()
def test_get_all_supply_chains(
    test_client_with_token,
):
    """
    Test that all supply chain objects are returned when an
    authorised request is made to the 'api/supply-chain' endpoint.
    """
    supply_chains = SupplyChainFactory.create_batch(4)
    num_chains = SupplyChain.objects.count()
    client = test_client_with_token
    url = reverse("supply-chain-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == num_chains
    assert response.data[0]["id"] == str(supply_chains[0].id)


@pytest.mark.django_db()
def test_get_all_supply_chain_from_a_given_government_department(
    test_client_with_token,
):
    """
    Test that when a government department id is given in query parameters,
    the '/api/supply-chain' endpoint returns a list of supply chains
    related to that government department.
    """
    gov_department = GovDepartmentFactory()
    supply_chain = SupplyChainFactory(gov_department=gov_department)
    # Create additional supply chain that is not linked to this gov department
    SupplyChainFactory()
    client = test_client_with_token
    response = client.get(
        "/api/supply-chains/", {"gov_department_id": gov_department.id}
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(supply_chain.id)


@pytest.mark.django_db()
def test_all_supply_chains_returned_if_query_param_empty(
    test_client_with_token,
):
    SupplyChainFactory.create_batch(5)
    num_chains = SupplyChain.objects.count()
    client = test_client_with_token
    response = client.get("/api/supply-chains/", {"supply_chain_id": ""})
    assert response.status_code == 200
    assert len(response.data) == num_chains


@pytest.mark.django_db()
def test_get_all_strategic_action_updates(
    test_client_with_token,
):
    """
    Test that all strategic action update objects are returned when an
    authorised request is made to the 'api/strategic-action-update' endpoint.
    """
    updates = StrategicActionUpdateFactory.create_batch(5)
    num_updates = StrategicActionUpdate.objects.count()
    client = test_client_with_token
    url = reverse("strategic-action-update-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == num_updates
    assert response.data[0]["id"] == str(updates[0].id)


@pytest.mark.django_db()
def test_filter_updates_by_strategic_action(
    test_client_with_token,
):
    """
    Test that when a strategic action id is given in query paramters,
    the '/api/strategic-action-updates' endpoint returns a list of updates
    related to that strategic action.
    """
    strategic_action = StrategicActionFactory()
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action,
    )
    # Create additional updates not linked to this strategic action
    StrategicActionUpdateFactory.create_batch(5)
    client = test_client_with_token
    response = client.get(
        "/api/strategic-action-updates/", {"strategic_action_id": strategic_action.id}
    )
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(strategic_action_update.id)


@pytest.mark.django_db()
def test_all_updates_returned_if_strat_action_id_empty(
    test_client_with_token,
):
    """
    Test that all strategic action update objects are returned
    when the 'strategic_action_id' query param is empty.
    """
    StrategicActionUpdateFactory.create_batch(5)
    num_updates = StrategicActionUpdate.objects.count()
    client = test_client_with_token
    response = client.get("/api/strategic-action-updates/", {"strategic_action_id": ""})
    assert response.status_code == 200
    assert len(response.data) == num_updates


@pytest.mark.parametrize(
    "filter_value, expected_num_objects",
    (("True", 1), ("true", 1), ("False", 2), ("false", 2), ("", 3)),
)
@pytest.mark.django_db()
def test_filter_updates_by_if_submitted(
    test_client_with_token,
    filter_value,
    expected_num_objects,
    test_in_progress_strategic_action_update,
    test_completed_strategic_action_update,
    test_submitted_strategic_action_update,
):
    """
    Test that when is_submitted is given in query paramters with a value of
    either true or false, the '/api/strategic-action-updates' endpoint returns
    the appropriate SrategicActionUpdate objects.
    When false, updates with a status of either completed or in_progress
    should be returned.
    """
    client = test_client_with_token
    response = client.get(
        "/api/strategic-action-updates/",
        {"is_submitted": filter_value},
    )
    assert response.status_code == 200
    assert len(response.data) == expected_num_objects
