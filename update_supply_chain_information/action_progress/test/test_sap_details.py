import pytest
from django.test import Client
from django.urls import reverse
from supply_chains.models import SupplyChain

from supply_chains.test.factories import StrategicActionFactory, SupplyChainFactory
from accounts.test.factories import GovDepartmentFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestSAPDetail:
    def test_auth(self):
        # Arrange
        # Act
        resp = Client().get(
            reverse(
                "action-progress-detail",
                kwargs={
                    "dept": "valid",
                    "supply_chain_slug": "valid_name",
                    "action_slug": "valid_data",
                },
            )
        )

        # Assert
        assert resp.status_code == 302

    def test_ogd_other_dept_error(self, logged_in_client):
        # Arrange
        dept_name = "other_dep"
        dept = GovDepartmentFactory(name=dept_name)
        sc_name = "ceramics"
        sc = SupplyChainFactory(gov_department=dept, name=sc_name)
        sa = StrategicActionFactory(supply_chain=sc)

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-detail",
                kwargs={
                    "dept": dept_name,
                    "supply_chain_slug": sc_name,
                    "action_slug": sa.slug,
                },
            )
        )

        # Assert
        assert resp.status_code == 403

    def test_auth_logged_in(self, logged_in_client, test_user):
        # Arrange
        dept = test_user.gov_department
        sc_name = "ceramics"
        sc = SupplyChainFactory(gov_department=dept, name=sc_name)
        sa = StrategicActionFactory(supply_chain=sc)

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-detail",
                kwargs={
                    "dept": dept.name,
                    "supply_chain_slug": sc_name,
                    "action_slug": sa.slug,
                },
            )
        )

        # Assert
        assert resp.status_code == 200

    def test_auth_invalid_sa(self, logged_in_client, test_user):
        # Arrange
        dept = test_user.gov_department
        sc_name = "ceramics"
        SupplyChainFactory(gov_department=dept, name=sc_name)

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-detail",
                kwargs={
                    "dept": dept,
                    "supply_chain_slug": sc_name,
                    "action_slug": "unknown",
                },
            )
        )

        assert resp.status_code == 404
