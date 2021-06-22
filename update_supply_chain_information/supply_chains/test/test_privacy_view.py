import pytest
from django.test import Client
from django.urls import reverse

from supply_chains.test.factories import (
    SupplyChainFactory,
    GovDepartmentFactory,
)


pytestmark = pytest.mark.django_db
# Status = StrategicActionUpdate.Status


# @pytest.fixture
# def taskcomp_stub(test_user):
#     sc_name = "Supply Chain 1"
#     sc = SupplyChainFactory.create(
#         name=sc_name,
#         gov_department=test_user.gov_department,
#         last_submission_date=date.today(),
#     )
#     scs = SupplyChainFactory.create_batch(
#         2, name=sc_name + "00", gov_department=test_user.gov_department
#     )
#     sa = StrategicActionFactory.create(supply_chain=sc)
#     StrategicActionUpdateFactory(
#         status=Status.SUBMITTED,
#         submission_date=date.today(),
#         strategic_action=sa,
#         supply_chain=sc,
#     )

#     yield {
#         "sc_name": sc_name,
#         "url": reverse(
#             "supply-chain-update-complete",
#             kwargs={"supply_chain_slug": slugify(sc_name)},
#         ),
#     }


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
