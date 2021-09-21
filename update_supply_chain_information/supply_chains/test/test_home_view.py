from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from supply_chains.test.factories import (
    SupplyChainFactory,
    GovDepartmentFactory,
)


pytestmark = pytest.mark.django_db


HOME_URL = reverse("index")


class TestHomePageView:
    def test_auth(self):
        # Arrange
        # Act
        resp = Client().get(HOME_URL)

        # Assert
        assert resp.status_code == 302

    def test_auth_no_perm(self, logged_in_client):
        # Arrange
        sc_name = "ceramics"
        dep = GovDepartmentFactory()
        SupplyChainFactory(gov_department=dep, name=sc_name)

        # Act
        resp = logged_in_client.get(HOME_URL)

        # Assert
        assert resp.status_code == 200

    def test_auth_logged_in(self, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(HOME_URL)

        # Assert
        assert resp.status_code == 200
