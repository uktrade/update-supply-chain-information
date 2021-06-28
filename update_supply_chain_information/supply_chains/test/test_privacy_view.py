import pytest
from django.test import Client
from django.urls import reverse

from supply_chains.test.factories import (
    SupplyChainFactory,
    GovDepartmentFactory,
)


pytestmark = pytest.mark.django_db


class TestPrivacyNoticeView:
    def test_auth(self):
        # Arrange
        # Act
        resp = Client().get(reverse("privacy"))

        # Assert
        assert resp.status_code == 302

    def test_auth_wo_perm(self, logged_in_client):
        # Arrange
        dep = GovDepartmentFactory()
        sc = SupplyChainFactory(gov_department=dep, name="ceramics")

        # Act
        resp = logged_in_client.get(reverse("privacy"))

        # Assert
        assert resp.status_code == 200

    def test_auth_logged_in(self, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(reverse("privacy"))

        # Assert
        assert resp.status_code == 200
