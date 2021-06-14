import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify

from supply_chains.test.factories import (
    SupplyChainFactory,
    GovDepartmentFactory,
    UserFactory,
)
from supply_chains.models import SupplyChain


pytestmark = pytest.mark.django_db
Rating = SupplyChain.StatusRating


@pytest.fixture
def sc_stub(test_user):
    sc_name = "Supply Chain 1"
    sc_con_name = "HelloWorld"
    sc_con_email = "hello@local"
    sc_vul_status = Rating.LOW
    sc_risk_status = Rating.MEDIUM
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
        "url": reverse("supply-chain-summary"),
    }


class TestSCSummaryView:
    def test_auth(self, sc_stub):
        # Arrange
        # Act
        resp = Client().get(sc_stub["url"])

        # Assert
        assert resp.status_code == 302

    def test_auth_no_perm(self, sc_stub, logged_in_client):
        # Arrange
        sc_name = "ceramics"
        dep = GovDepartmentFactory()
        UserFactory(gov_department=dep)
        SupplyChainFactory(gov_department=dep, name=sc_name)

        # Act
        resp = logged_in_client.get(sc_stub["url"])

        # Assert
        assert resp.status_code == 200
        assert len(resp.context["supply_chains"]) == 1
        assert resp.context["supply_chains"][0].name == sc_stub["sc_name"]

    def test_auth_logged_in(self, sc_stub, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(sc_stub["url"])

        # Assert
        assert resp.status_code == 200
        assert resp.context["supply_chains"][0].name == sc_stub["sc_name"]

    def test_sc_summary(self, logged_in_client, sc_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(sc_stub["url"])

        # Assert
        assert resp.context["supply_chains"][0].contact_name == sc_stub["sc_con_name"]
        assert resp.context["supply_chains"][0].contact_email == sc_stub["sc_con_email"]
        assert (
            resp.context["supply_chains"][0].vulnerability_status
            == sc_stub["sc_vul_status"]
        )
        assert (
            resp.context["supply_chains"][0].risk_severity_status
            == sc_stub["sc_risk_status"]
        )

    def test_sc_summary_multiple(self, logged_in_client, test_user):
        # Arrange
        SupplyChainFactory.create_batch(4, gov_department=test_user.gov_department)

        # Act
        resp = logged_in_client.get(reverse("supply-chain-summary"))

        # Assert
        assert resp.status_code == 200
        assert resp.context["supply_chains"].paginator.count == 4

    @pytest.mark.parametrize(
        "num_scs, url, pages_returned, objects_returned",
        (
            (
                2,
                reverse("supply-chain-summary"),
                1,
                2,
            ),
            (7, reverse("supply-chain-summary"), 2, 5),
            (7, reverse("supply-chain-summary") + "?page=2", 2, 2),
        ),
    )
    def test_pagination(
        self,
        logged_in_client,
        test_user,
        num_scs,
        url,
        pages_returned,
        objects_returned,
    ):
        # Arrange
        SupplyChainFactory.create_batch(
            num_scs, gov_department=test_user.gov_department
        )

        # Act
        resp = logged_in_client.get(url)

        # Assert
        p = resp.context["supply_chains"]

        assert resp.status_code == 200
        assert p.paginator.num_pages == pages_returned
        assert len(p.object_list) == objects_returned
