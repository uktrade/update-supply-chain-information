from datetime import date, timedelta

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import User
from accounts.test.factories import GovDepartmentFactory
from supply_chains.models import SupplyChain
from supply_chains.test.factories import StrategicActionFactory, SupplyChainFactory

pytestmark = pytest.mark.django_db


def test_homepage_user_redirected():
    """Test unauthenticated client is redirected from homepage."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 302


@pytest.mark.parametrize(
    "num_supply_chains, url, num_supply_chains_returned",
    ((4, "/", 4), (7, "/", 5), (7, "/?page=2", 2)),
)
def test_homepage_pagination(
    num_supply_chains, logged_in_client, test_user, url, num_supply_chains_returned
):
    """
    Test correct number of supply chains are passed to homepage via context
    depending on total number linked to the user's department.
    """
    SupplyChainFactory.create_batch(
        num_supply_chains, gov_department=test_user.gov_department
    )
    response = logged_in_client.get(url)
    assert response.status_code == 200
    assert response.context["gov_department_name"] == test_user.gov_department.name
    assert len(response.context["supply_chains"]) == num_supply_chains_returned


def test_homepage_update_complete(logged_in_client, test_user):
    """
    Test update_complete is True in context passed to homepage when all supply chains
    linked to the user's gov department have a last_submission date after last deadline.
    """
    SupplyChainFactory.create_batch(
        6, gov_department=test_user.gov_department, last_submission_date=date.today()
    )
    response = logged_in_client.get("/")
    assert response.status_code == 200
    assert response.context["update_complete"]
    assert response.context["num_updated_supply_chains"] == 6


def test_homepage_update_incomplete(logged_in_client, test_user):
    """
    Test update_complete is False in context passed to homepage when not all supply
    chains linked to the user's gov department have a last_submission date after
    last deadline.
    """
    SupplyChainFactory.create_batch(
        3, gov_department=test_user.gov_department, last_submission_date=date.today()
    )
    SupplyChainFactory.create_batch(
        3,
        gov_department=test_user.gov_department,
        last_submission_date=date.today() - timedelta(35),
    )
    response = logged_in_client.get("/")
    assert response.status_code == 200
    assert not response.context["update_complete"]
    assert response.context["num_updated_supply_chains"] == 3


def test_strat_action_summary_page_unauthenticated(test_supply_chain):
    """Test unauthenticated request is redirected."""
    client = Client()
    response = client.get(reverse("strat_action_summary", args=[test_supply_chain.id]))
    assert response.status_code == 302


def test_strat_action_summary_page_unauthorised(
    logged_in_client, test_user, test_supply_chain
):
    """Test unauthorised request.

    A user not linked to the same gov department as a
    supply chain cannot access the strategic action summary
    page for that supply chain.
    """
    dep = GovDepartmentFactory()
    sc = SupplyChainFactory(gov_department=dep)
    response = logged_in_client.get(
        reverse("strat_action_summary", args=[test_supply_chain.slug])
    )
    assert response.status_code == 403


def test_strat_action_summary_page_success(logged_in_client, test_user):
    """Test authenticated request.

    When an authorised request is made to the strategic_action_summary URL,
    from a user linked to the same gov department as the strategic actions,
    the correct supply chain and only un_archived strategic actions are
    returned in context.
    """
    sc = SupplyChainFactory(gov_department=test_user.gov_department)
    StrategicActionFactory.create_batch(5, supply_chain=sc)
    StrategicActionFactory.create_batch(
        2, supply_chain=sc, is_archived=True, archived_reason="A reason"
    )
    response = logged_in_client.get(reverse("strat_action_summary", args=[sc.slug]))
    assert response.status_code == 200
    assert response.context["supply_chain"] == sc
    assert len(response.context["strategic_actions"]) == 5


def test_strat_action_summary_page_pagination(logged_in_client, test_user):
    """Test pagination of strategic actions returned in context."""
    sc = SupplyChainFactory(gov_department=test_user.gov_department)
    StrategicActionFactory.create_batch(14, supply_chain=sc)
    response = logged_in_client.get(
        "%s?page=3" % reverse("strat_action_summary", args=[sc.slug])
    )
    assert response.status_code == 200
    assert len(response.context["strategic_actions"]) == 4
