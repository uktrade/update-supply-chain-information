import pytest
from django.test import Client
from django.urls import reverse

from supply_chains.test.factories import SupplyChainFactory
from accounts.test.factories import GovDepartmentFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestSAPFilters:
    def test_auth(self):
        # Arrange
        # Act
        resp = Client().get(reverse("action-progress"))

        # Assert
        assert resp.status_code == 302

    def test_auth_no_perm(self, logged_in_client):
        # Arrange
        other_dept = "mod"

        # Act
        resp = logged_in_client.get(
            reverse("action-progress-department", kwargs={"dept": other_dept})
        )

        # Assert
        assert resp.status_code == 403

    def test_auth_invalid_dept(self, logged_in_client):
        # Arrange
        dept = "unknown"

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-department",
                kwargs={"dept": dept},
            )
        )

        # Assert
        assert resp.status_code == 403

    def test_ogd_other_dept_error(self, logged_in_client):
        # Arrange
        dept_name = "other_dep"
        dept = GovDepartmentFactory(name=dept_name)
        u = UserFactory(gov_department=dept)

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-department",
                kwargs={"dept": dept_name},
            )
        )

        # Assert
        assert resp.status_code == 403

    def test_auth_invalid_sc(self, logged_in_client, test_user):
        # Arrange
        dept = test_user.gov_department
        inv_sc_slug = "unknown"

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-list",
                kwargs={"dept": dept, "supply_chain_slug": inv_sc_slug},
            )
        )

        assert resp.status_code == 404

    def test_auth_logged_in(self, logged_in_client, test_user):
        # Arrange
        dept = test_user.gov_department

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-department",
                kwargs={"dept": dept},
            )
        )

        # Assert
        assert resp.status_code == 200
        # brute force method to verify missing Dep filter :-)
        assert "hidden" in resp.rendered_content

    def test_sc_filter(self, logged_in_client, test_user):
        # Arrange
        dept = test_user.gov_department
        sc_name = "ceramics"
        SupplyChainFactory(name=sc_name)

        # Act
        resp = logged_in_client.get(
            reverse(
                "action-progress-list",
                kwargs={"dept": dept, "supply_chain_slug": sc_name},
            )
        )

        # Assert
        assert resp.status_code == 200
