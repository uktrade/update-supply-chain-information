from datetime import date, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify

from supply_chains.models import SupplyChain, StrategicActionUpdate
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
)


pytestmark = pytest.mark.django_db
Status = StrategicActionUpdate.Status


@pytest.fixture
def taskcomp_stub(test_user):
    sc_name = "Supply Chain 1"
    sc = SupplyChainFactory.create(
        name=sc_name,
        gov_department=test_user.gov_department,
        last_submission_date=date.today() - timedelta(days=10),
    )
    scs = SupplyChainFactory.create_batch(
        2, name=sc_name + "00", gov_department=test_user.gov_department
    )
    sa = StrategicActionFactory.create(supply_chain=sc)
    StrategicActionUpdateFactory(
        status=Status.SUBMITTED,
        submission_date=date.today(),
        strategic_action=sa,
        supply_chain=sc,
    )

    yield {
        "sc_name": sc_name,
        "url": reverse("tcomplete", kwargs={"sc_slug": slugify(sc_name)}),
    }


class TestTaskCompleteView:
    # TODO: Fix this!
    @pytest.mark.skip
    def test_auth(self, taskcomp_stub):
        # Arrange
        # Act
        resp = Client().get(taskcomp_stub["url"])

        # Assert
        assert resp.status_code == 302

    def test_auth_logged_in(self, taskcomp_stub, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(taskcomp_stub["url"])

        # Assert
        v = resp.context["view"]
        assert resp.status_code == 200
        assert v.supply_chain.name == taskcomp_stub["sc_name"]

    def test_action_summary(self, logged_in_client, taskcomp_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(taskcomp_stub["url"])

        # Assert
        v = resp.context["view"]
        assert v.sum_of_supply_chains == 3
        assert v.num_updated_supply_chains == 1
