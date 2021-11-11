import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import GovDepartment
from accounts.test.factories import GovDepartmentFactory, UserFactory
from supply_chains.test.factories import SupplyChainFactory, ScenarioAssessmentFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def logged_in_ogd():
    dept = GovDepartmentFactory(name="OGD")
    user = UserFactory(first_name="joe", gov_department=dept)

    client = Client()
    client.force_login(user)

    yield client


class TestSCDInfo:
    def test_auth(self, test_user):
        # Arrange
        sc = SupplyChainFactory.create()

        # Act
        resp = Client().get(
            reverse(
                "chain-details-info",
                kwargs={"dept": test_user.gov_department, "supply_chain_slug": sc.slug},
            )
        )

        # Assert
        assert resp.status_code == 302

    def test_ogd_other_dept(self, logged_in_ogd):
        # Arrange
        dept_name = "other_dep"
        dept = GovDepartmentFactory(name=dept_name)
        sc = SupplyChainFactory.create(gov_department=dept)

        # Act
        resp = logged_in_ogd.get(
            reverse(
                "chain-details-info",
                kwargs={"dept": dept_name, "supply_chain_slug": sc.slug},
            )
        )

        # Assert
        assert resp.status_code == 200

    def test_auth_on_dept(self, logged_in_client):
        # Arrange
        dept_name = "other_dep"
        dept = GovDepartmentFactory(name=dept_name)
        sc = SupplyChainFactory.create(gov_department=dept)

        # Act
        resp = logged_in_client.get(
            reverse(
                "chain-details-info",
                kwargs={"dept": dept_name, "supply_chain_slug": sc.slug},
            )
        )

        # Assert
        assert resp.status_code == 200

    def test_auth_success(self, logged_in_client, test_user):
        # Arrange
        sc = SupplyChainFactory.create()

        # Act
        resp = logged_in_client.get(
            reverse(
                "chain-details-info",
                kwargs={"dept": test_user.gov_department, "supply_chain_slug": sc.slug},
            )
        )

        # Assert
        assert resp.status_code == 200

    def test_unknown_dept(self, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(
            reverse(
                "chain-details-info",
                kwargs={"dept": "unknown", "supply_chain_slug": "unknown"},
            )
        )

        # Assert
        assert resp.status_code == 404

    def test_supply_chain_scenario_assessment_is_optional(self, logged_in_ogd):
        # Arrange
        dept = GovDepartment.objects.first()
        sc = SupplyChainFactory.create(gov_department=dept)

        # Act
        resp = logged_in_ogd.get(
            reverse(
                "chain-details-info",
                kwargs={"dept": dept.name, "supply_chain_slug": sc.slug},
            )
        )

        # Assert
        assert resp.status_code == 200
        assert not hasattr(resp.context["sc"], "scenario_assessment")
