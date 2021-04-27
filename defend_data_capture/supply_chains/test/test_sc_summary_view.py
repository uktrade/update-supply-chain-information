from datetime import date, timedelta

import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify

from supply_chains.models import SupplyChain
from supply_chains.test.factories import SupplyChainFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def sc_stub(test_user):
    sc_name = "Supply Chain 1"
    sc_con_name = "HelloWorld"
    sc_con_email = "hello@local"
    sc_vul_status = "Low"
    sc_risk_status = "Medium"
    sc = SupplyChainFactory.create(
        name=sc_name,
        gov_department=test_user.gov_department,
        contact_name=sc_con_name,
        contact_email=sc_con_email,
        vulnerability_status=sc_vul_status,
        risk_severity_status=sc_risk_status,
    )
    yield {
        "sc_name": sc_name,
        "sc_con_name": sc_con_name,
        "sc_con_email": sc_con_email,
        "sc_vul_status": sc_vul_status,
        "sc_risk_status": sc_risk_status,
        "url": reverse("sc_summary", kwargs={"sc_slug": slugify(sc_name)}),
    }


class TestSCSummaryView:
    def test_auth(self, sc_stub):
        # Arrange
        # Act
        resp = Client().get(sc_stub["url"])

        # Assert
        assert resp.status_code == 302

    def test_auth_logged_in(self, sc_stub, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(sc_stub["url"])

        # Assert
        assert resp.status_code == 200
        assert resp.context["supply_chain"].name == sc_stub["sc_name"]

    def test_sc_summary(self, logged_in_client, sc_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(sc_stub["url"])

        # Assert
        assert resp.context["supply_chain"].contact_name == sc_stub["sc_con_name"]
        assert resp.context["supply_chain"].contact_email == sc_stub["sc_con_email"]
        assert (
            resp.context["supply_chain"].vulnerability_status
            == sc_stub["sc_vul_status"]
        )
        assert (
            resp.context["supply_chain"].risk_severity_status
            == sc_stub["sc_risk_status"]
        )
