from datetime import date

import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify

from supply_chains.models import StrategicActionUpdate
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
    GovDepartmentFactory,
)


pytestmark = pytest.mark.django_db
Status = StrategicActionUpdate.Status


@pytest.fixture
def taskcomp_stub(test_user):
    sc_name = "Supply Chain 1"
    sc = SupplyChainFactory.create(
        name=sc_name,
        gov_department=test_user.gov_department,
        last_submission_date=date.today(),
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
        "url": reverse(
            "supply-chain-update-complete",
            kwargs={"supply_chain_slug": slugify(sc_name)},
        ),
    }


class TestTaskCompleteView:
    def test_auth(self, taskcomp_stub):
        # Arrange
        # Act
        resp = Client().get(taskcomp_stub["url"])

        # Assert
        assert resp.status_code == 302

    def test_auth_no_perm(self, logged_in_client):
        # Arrange
        sc_name = "ceramics"
        dep = GovDepartmentFactory()
        sc = SupplyChainFactory(gov_department=dep, name=sc_name)

        # Act
        resp = logged_in_client.get(
            reverse(
                "supply-chain-update-complete",
                kwargs={"supply_chain_slug": slugify(sc_name)},
            )
        )

        # Assert
        assert resp.status_code == 403

    def test_auth_logged_in(self, taskcomp_stub, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(taskcomp_stub["url"])

        # Assert
        assert resp.status_code == 200
        print(f'view: {resp.context["view"]}')
        assert resp.context["view"].supply_chain.name == taskcomp_stub["sc_name"]

    def test_action_summary(self, logged_in_client, taskcomp_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(taskcomp_stub["url"])

        # Assert
        assert resp.context["view"].sum_of_supply_chains == 3
        assert resp.context["view"].num_updated_supply_chains == 1
