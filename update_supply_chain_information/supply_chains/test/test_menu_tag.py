from datetime import date


import pytest
from django.urls import reverse

from supply_chains.models import StrategicActionUpdate
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
)
from supply_chains.templatetags.supply_chain_tags import get_active_menu as sut

pytestmark = pytest.mark.django_db
Status = StrategicActionUpdate.Status

sc_name = "ceramics"
sa_name = "production"
sau_slug = "01-2020"


@pytest.fixture
def model_stub(test_user):
    sc = SupplyChainFactory.create(
        name=sc_name,
        gov_department=test_user.gov_department,
        last_submission_date=date.today(),
    )
    sa = StrategicActionFactory.create(supply_chain=sc, name=sa_name)
    StrategicActionUpdateFactory(
        status=Status.SUBMITTED,
        submission_date=date(day=1, month=1, year=2020),
        strategic_action=sa,
        supply_chain=sc,
    )


class TestActiveMenuTag:
    def test_no_active_menu(self, logged_in_client):
        # Arrange
        resp = logged_in_client.get(
            reverse(
                "privacy",
            )
        )

        # Act
        menu = sut(resp.context)

        # Assert
        assert menu == None

    def test_home_menu(self, logged_in_client):
        # Arrange
        resp = logged_in_client.get(
            reverse(
                "index",
            )
        )

        # Act
        menu = sut(resp.context)

        # Assert
        assert menu == "home"

    @pytest.mark.parametrize(
        "url_name, args",
        (
            ("sc-home", {}),
            ("supply-chain-summary", {}),
            ("supply-chain-task-list", {"supply_chain_slug": sc_name}),
            ("supply-chain-summary", {"supply_chain_slug": sc_name}),
            ("strategic-action-summary", {"supply_chain_slug": sc_name}),
            (
                "monthly-update-info-edit",
                {
                    "supply_chain_slug": sc_name,
                    "action_slug": sa_name,
                    "update_slug": sau_slug,
                },
            ),
        ),
    )
    def test_updates_menu(self, logged_in_client, model_stub, url_name, args):
        # Arrange
        resp = logged_in_client.get(reverse(url_name, kwargs=args))

        # Act
        menu = sut(resp.context)

        # Assert
        assert menu == "updates"

    @pytest.mark.parametrize(
        "url_name, args",
        (
            ("action-progress", {}),
            ("action-progress-department", {}),
            ("action-progress-list", {"supply_chain_slug": sc_name}),
            (
                "action-progress-detail",
                {"supply_chain_slug": sc_name, "action_slug": sa_name},
            ),
        ),
    )
    def test_sap_menu(self, logged_in_client, model_stub, test_user, url_name, args):
        # Arrange
        if url_name != "action-progress":
            args.update({"dept": test_user.gov_department.name})

        resp = logged_in_client.get(reverse(url_name, kwargs=args))

        # Act
        menu = sut(resp.context)

        # Assert
        assert menu == "sap"

    @pytest.mark.parametrize(
        "url_name, args",
        (
            ("chain-details", {}),
            ("chain-details-list", {}),
        ),
    )
    def test_scd_menu(self, logged_in_client, model_stub, test_user, url_name, args):
        # Arrange
        if url_name != "chain-details":
            args.update({"dept": test_user.gov_department.name})

        resp = logged_in_client.get(reverse(url_name, kwargs=args))

        # Act
        menu = sut(resp.context)

        # Assert
        assert menu == "scd"
