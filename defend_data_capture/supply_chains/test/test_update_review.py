from datetime import date, datetime

import pytest
from django.test import Client
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.template.defaultfilters import date as date_filter

from supply_chains.models import StrategicActionUpdate
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
    GovDepartmentFactory,
)


pytestmark = pytest.mark.django_db
Status = StrategicActionUpdate.Status


@pytest.fixture
def update_stub(test_user):
    sc_name = "Supply Chain 1"
    sa_name = "action 01"
    sa_completion = "2021-02-01"
    update_slug = "05-2021"
    sau_rag = "Amber"
    sau_reason = "Brexit negotiations"

    sc = SupplyChainFactory.create(
        name=sc_name,
        gov_department=test_user.gov_department,
        last_submission_date=date.today(),
    )
    sa = StrategicActionFactory.create(
        name=sa_name, supply_chain=sc, target_completion_date=sa_completion
    )
    StrategicActionUpdateFactory(
        slug=update_slug,
        status=Status.SUBMITTED,
        submission_date=date.today(),
        strategic_action=sa,
        supply_chain=sc,
        implementation_rag_rating=sau_rag,
        reason_for_delays=sau_reason,
    )

    yield {
        "sc": sc,
        "sa": sa,
        "sc_name": sc_name,
        "sa_name": sa_name,
        "sa_completion": sa_completion,
        "sau_rag": sau_rag,
        "sau_reason": sau_reason,
        "update_slug": update_slug,
        "url": reverse(
            "update_review",
            kwargs={
                "supply_chain_slug": slugify(sc_name),
                "action_slug": slugify(sa_name),
                "update_slug": update_slug,
            },
        ),
    }


class TestSAUReview:
    def test_auth(self, update_stub):
        # Arrange
        # Act
        resp = Client().get(update_stub["url"])

        # Assert
        assert resp.status_code == 302

    def test_auth_no_perm(self, logged_in_client):
        # Arrange
        sc_name = "ceramics"
        dep = GovDepartmentFactory()
        sc = SupplyChainFactory(gov_department=dep, name=sc_name)
        sa = StrategicActionFactory.create(supply_chain=sc)
        sau = StrategicActionUpdateFactory(
            status=Status.SUBMITTED,
            submission_date=date.today(),
            strategic_action=sa,
            supply_chain=sc,
        )

        # Act
        resp = logged_in_client.get(
            reverse(
                "update_review",
                kwargs={
                    "supply_chain_slug": slugify(sc_name),
                    "action_slug": sa.slug,
                    "update_slug": sau.slug,
                },
            )
        )

        # Assert
        assert resp.status_code == 403

    def test_auth_logged_in(self, update_stub, logged_in_client):
        # Arrange
        # Act
        resp = logged_in_client.get(update_stub["url"])

        # Assert
        assert resp.status_code == 200
        assert resp.context["strategic_action"].name == update_stub["sa_name"]

    def test_update_details(self, logged_in_client, update_stub):
        # Arrange
        # Act
        resp = logged_in_client.get(update_stub["url"])

        # Assert
        assert resp.context["supply_chain"].name == update_stub["sc_name"]
        assert resp.context["completion_estimation"] == date_filter(
            datetime.strptime(update_stub["sa_completion"], r"%Y-%m-%d"), "d F Y"
        )
        assert (
            resp.context["update"].implementation_rag_rating == update_stub["sau_rag"]
        )
        assert resp.context["update"].reason_for_delays == update_stub["sau_reason"]
        assert resp.context["update"].submission_date.strftime(
            r"%d.%m.%Y"
        ) == date_filter(date.today(), "d.m.Y")

    def test_update_details_ongoing(self, logged_in_client, test_user):
        # Arrange
        sc_name = "ceramics"
        sa_name = "action 01"
        update_slug = "05-2021"
        sc = SupplyChainFactory.create(
            name=sc_name,
            gov_department=test_user.gov_department,
            last_submission_date=date.today(),
        )
        sa = sa = StrategicActionFactory.create(
            name=sa_name, supply_chain=sc, is_ongoing=True
        )
        StrategicActionUpdateFactory(
            slug=update_slug,
            status=Status.SUBMITTED,
            submission_date=date.today(),
            strategic_action=sa,
            supply_chain=sc,
        )

        # Act
        resp = logged_in_client.get(
            reverse(
                "update_review",
                kwargs={
                    "supply_chain_slug": sc_name,
                    "action_slug": slugify(sa_name),
                    "update_slug": update_slug,
                },
            )
        )

        # Assert
        assert resp.context["supply_chain"].name == sc_name
        assert resp.context["completion_estimation"] == "Ongoing"
