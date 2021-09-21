import pytest
from django.test import Client
from django.urls import reverse

from accounts.test.factories import GovDepartmentFactory, UserFactory


pytestmark = pytest.mark.django_db


class TestSCDFilter:
    def test_auth(self):
        # Arrange
        # Act
        resp = Client().get(reverse("chain-details"))

        # Assert
        assert resp.status_code == 302

    def test_auth_on_dept(self):
        # Arrange
        dept_name = "other_dep"
        dept = GovDepartmentFactory(name=dept_name)

        # Act
        resp = Client().get(
            reverse(
                "chain-details-list",
                kwargs={"dept": dept_name},
            )
        )

        # Assert
        assert resp.status_code == 302

    def test_auth_success(self, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(reverse("chain-details"))

        # Assert
        assert resp.status_code == 200

    def test_auth_own_dept(self, logged_in_client, test_user):
        # Arrange
        # Act
        resp = logged_in_client.get(
            reverse("chain-details-list", kwargs={"dept": test_user.gov_department})
        )

        # Assert
        assert resp.status_code == 200

    def test_ogd_other_dept(self, logged_in_client):
        # Arrange
        dept_name = "other_dep"
        dept = GovDepartmentFactory(name=dept_name)
        u = UserFactory(gov_department=dept)

        # Act
        resp = logged_in_client.get(
            reverse(
                "chain-details-list",
                kwargs={"dept": dept_name},
            )
        )

        # Assert
        assert resp.status_code == 200

    def test_unknown_dept(self, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(
            reverse(
                "chain-details-list",
                kwargs={"dept": "unknown"},
            )
        )

        # Assert
        assert resp.status_code == 404
