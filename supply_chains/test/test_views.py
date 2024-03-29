from unittest import mock
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

import pytest
from django.db.models.query import QuerySet
from django.test import Client
from django.urls import reverse

from accounts.models import GovDepartment
from accounts.test.factories import GovDepartmentFactory
from supply_chains.forms import YesNoChoices, ApproximateTimings
from supply_chains.models import StrategicAction, StrategicActionUpdate
from supply_chains.test.factories import (
    StrategicActionUpdateFactory,
)
from supply_chains.models import SupplyChain
from supply_chains.test.factories import StrategicActionFactory, SupplyChainFactory

pytestmark = pytest.mark.django_db


def test_sc_homepage_user_redirected():
    """Test unauthenticated client is redirected from homepage."""
    client = Client()
    response = client.get("/")
    assert response.status_code == 302


@pytest.mark.parametrize(
    "num_supply_chains, url, num_supply_chains_returned",
    (
        (4, "/supply-chains/", 4),
        (7, "/supply-chains/", 5),
        (7, "/supply-chains/?page=2", 2),
    ),
)
def test_sc_homepage_pagination(
    num_supply_chains, logged_in_client, test_user, url, num_supply_chains_returned
):
    """Test pagination of supply chains on homepage.

    Check the correct number of supply chains are passed to homepage
    via context depending on total number linked to the user's department,
    and that the supply chains are annotated with 'strategic_action_count'.
    """
    SupplyChainFactory.create_batch(
        num_supply_chains, gov_department=test_user.gov_department
    )
    response = logged_in_client.get(url)
    assert response.status_code == 200
    assert response.context["gov_department_name"] == test_user.gov_department.name
    assert len(response.context["supply_chains"]) == num_supply_chains_returned


def test_sc_homepage_update_complete(logged_in_client, test_user):
    """Test update_complete is True.

    'update_complete' should be True in context passed to homepage when all supply
    chains linked to the user's gov department have a last_submission date after
    last deadline.
    """
    # Arrange
    for _ in range(6):
        sc = SupplyChainFactory(
            gov_department=test_user.gov_department, last_submission_date=date.today()
        )
        StrategicActionFactory(supply_chain=sc)

    # Act
    response = logged_in_client.get("/supply-chains/")

    # Assert
    assert response.status_code == 200
    assert response.context["update_complete"]
    assert response.context["num_updated_supply_chains"] == 6
    assert "Your monthly update is complete" not in response.rendered_content
    assert 'class="govuk-notification-banner"' in response.rendered_content
    assert (
        "All supply chains have been completed for this month"
        in response.rendered_content
    )
    assert "Complete your monthly update" not in response.rendered_content
    assert (
        "Select a supply chain to provide your regular monthly update"
        not in response.rendered_content
    )


def test_sc_homepage_update_incomplete(logged_in_client, test_user):
    """Test update_complete is False.

    'update_complete' should be False in context passed to homepage when not all
    supply chains linked to the user's gov department have a last_submission date
    after last deadline.
    """
    # Arrange
    for _ in range(3):
        sc = SupplyChainFactory(
            gov_department=test_user.gov_department, last_submission_date=date.today()
        )
        StrategicActionFactory(supply_chain=sc)

        sc2 = SupplyChainFactory(
            gov_department=test_user.gov_department,
            last_submission_date=date.today() - timedelta(35),
        )
        StrategicActionFactory(supply_chain=sc2)

    # Act
    response = logged_in_client.get("/supply-chains/")

    # Assert
    assert response.status_code == 200
    assert not response.context["update_complete"]
    assert response.context["num_updated_supply_chains"] == 3
    assert response.context["num_in_prog_supply_chains"] == 3
    assert "Complete your monthly update" not in response.rendered_content
    assert (
        "Select a supply chain to provide your regular monthly update"
        in response.rendered_content
    )

    assert "Your monthly update is complete" not in response.rendered_content
    assert (
        "All supply chains have been completed for this month"
        not in response.rendered_content
    )


def test_sc_homepage_filters_out_archived_supply_chains(logged_in_client, test_user):
    gov_department = test_user.gov_department
    # Create archived supply chains
    SupplyChainFactory.create_batch(
        5, gov_department=gov_department, is_archived=True, archived_reason="Reason"
    )
    # Create non archived supply chains
    SupplyChainFactory.create_batch(5, gov_department=gov_department)

    num_unarchived_supply_chains = SupplyChain.objects.filter(is_archived=False).count()
    response = logged_in_client.get(reverse("sc-home"))

    assert len(response.context["supply_chains"]) == num_unarchived_supply_chains


def test_sc_homepage_filters_out_archived_SAs(logged_in_client, test_user):
    # Arrange
    sc = SupplyChainFactory(
        name="Medical",
        gov_department=test_user.gov_department,
    )
    archived_count = 0
    sas = StrategicActionFactory.create_batch(10, supply_chain=sc)
    for i in range(len(sas)):
        if i % 2 == 0:
            archived_count += 1
            sas[i].is_archived = True
            sas[i].archived_reason = "Reason"
            sas[i].save()

    # Act
    resp = logged_in_client.get(reverse("sc-home"))

    # Assert
    supply_chain = resp.context["supply_chains"].object_list[0]
    assert supply_chain["sa_count"] == archived_count


def test_sc_homepage_summary_with_archived_SAs(logged_in_client, test_user):
    # Arrange
    active_sa = SupplyChainFactory(
        name="Medical",
        gov_department=test_user.gov_department,
    )
    sc = SupplyChainFactory(
        name="carbon",
        gov_department=test_user.gov_department,
    )

    StrategicActionFactory.create_batch(5, supply_chain=active_sa)
    StrategicActionFactory.create_batch(
        3, supply_chain=sc, is_archived=True, archived_reason="Reason"
    )

    # Act
    resp = logged_in_client.get(reverse("sc-home"))

    # Assert
    assert resp.context["update_complete"] == False
    assert resp.context["num_in_prog_supply_chains"] == 1
    assert len(resp.context["supply_chains"]) == 2


def test_sc_homepage_summary_complete_with_archived_SAs(logged_in_client, test_user):
    # Arrange
    active_sa = SupplyChainFactory(
        name="Medical",
        gov_department=test_user.gov_department,
    )
    sc = SupplyChainFactory(
        name="carbon",
        gov_department=test_user.gov_department,
    )

    sa = StrategicActionFactory(supply_chain=active_sa)
    StrategicActionFactory.create_batch(
        3, supply_chain=sc, is_archived=True, archived_reason="Reason"
    )

    StrategicActionUpdateFactory()
    dummy_qs = QuerySet(model=StrategicActionUpdate)

    # Act
    with mock.patch(
        "supply_chains.models.SupplyChainQuerySet.submitted_since",
        return_value=dummy_qs,
    ):
        resp = logged_in_client.get(reverse("sc-home"))

    # Assert
    assert resp.context["update_complete"]
    assert resp.context["num_in_prog_supply_chains"] == 0
    assert len(resp.context["supply_chains"]) == 2


def test_strat_action_summary_page_unauthenticated(test_supply_chain):
    """Test unauthenticated request is redirected."""
    client = Client()
    response = client.get(
        reverse("strategic-action-summary", args=[test_supply_chain.id])
    )
    assert response.status_code == 302


def test_strat_action_summary_page_unauthorised(
    logged_in_client, test_user, test_supply_chain
):
    """Test unauthorised request.

    A user not linked to the same gov department as a
    supply chain cannot access the strategic action summary
    page for that supply chain.
    """
    dep = GovDepartmentFactory()
    sc = SupplyChainFactory(gov_department=dep)
    response = logged_in_client.get(
        reverse("strategic-action-summary", args=[test_supply_chain.slug])
    )
    assert response.status_code == 403


def test_strat_action_summary_page_success(logged_in_client, test_user):
    """Test authenticated request.

    When an authorised request is made to the strategic_action_summary URL,
    from a user linked to the same gov department as the strategic actions,
    the correct supply chain and only un_archived strategic actions are
    returned in context.
    """
    sc = SupplyChainFactory(gov_department=test_user.gov_department)
    StrategicActionFactory.create_batch(5, supply_chain=sc)
    StrategicActionFactory.create_batch(
        2, supply_chain=sc, is_archived=True, archived_reason="A reason"
    )
    response = logged_in_client.get(reverse("strategic-action-summary", args=[sc.slug]))
    assert response.status_code == 200
    assert response.context["supply_chain"] == sc
    assert len(response.context["strategic_actions"]) == 5


def test_strat_action_summary_page_pagination(logged_in_client, test_user):
    """Test pagination of strategic actions returned in context."""
    sc = SupplyChainFactory(gov_department=test_user.gov_department)
    StrategicActionFactory.create_batch(14, supply_chain=sc)
    response = logged_in_client.get(
        "%s?page=3" % reverse("strategic-action-summary", args=[sc.slug])
    )
    assert response.status_code == 200
    assert len(response.context["strategic_actions"]) == 4


class TestMonthlyUpdateTimingPage:
    def test_posting_form_saves_changed_target_completion_date_to_strategic_action_update(
        self, logged_in_client, test_user
    ):
        supply_chain: SupplyChain = SupplyChainFactory()
        test_user.gov_department = supply_chain.gov_department
        test_user.save()
        strategic_action: StrategicAction = StrategicActionFactory(
            supply_chain=supply_chain
        )
        strategic_action.target_completion_date = None
        strategic_action.is_ongoing = True
        strategic_action.save()
        strategic_action_update: StrategicActionUpdate = StrategicActionUpdateFactory(
            strategic_action=strategic_action,
            status=StrategicActionUpdate.Status.IN_PROGRESS,
            supply_chain=strategic_action.supply_chain,
            reason_for_completion_date_change="All things must pass.",
        )

        mock_today = date(year=2021, month=4, day=23)
        with mock.patch(
            "supply_chains.forms.date",
            mock.Mock(today=mock.Mock(return_value=mock_today)),
        ):
            expected_target_completion_date = mock_today + relativedelta(years=+1)
            form_data = {
                "is_completion_date_known": YesNoChoices.NO,
                f"{YesNoChoices.NO}-surrogate_is_ongoing": ApproximateTimings.ONE_YEAR,
            }
            url_kwargs = {
                "supply_chain_slug": strategic_action.supply_chain.slug,
                "action_slug": strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            }
            url = reverse("monthly-update-timing-edit", kwargs=url_kwargs)
            response = logged_in_client.post(url, form_data)
            assert response.status_code == 302
            strategic_action.refresh_from_db()
            assert strategic_action.target_completion_date is None
            strategic_action_update.refresh_from_db()
            assert (
                strategic_action_update.changed_value_for_target_completion_date
                == expected_target_completion_date
            )


class TestNoCompletionDateMonthlyUpdateNavigationItems:
    def setup_method(self, *args, **kwargs):
        self.supply_chain = SupplyChainFactory()
        self.strategic_action = StrategicActionFactory(supply_chain=self.supply_chain)
        self.strategic_action_update = StrategicActionUpdateFactory(
            strategic_action=self.strategic_action,
            supply_chain=self.strategic_action.supply_chain,
        )

    def test_info_view_has_info_timing_status_summary_links(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action.target_completion_date = None
        self.strategic_action.save()
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "is_current_page" in navigation_links["Info"]
        assert "Timing" in navigation_links
        assert "Status" in navigation_links
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links

    def test_timing_view_has_info_timing_status_summary_links(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-timing-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action.target_completion_date = None
        self.strategic_action.save()
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" in navigation_links
        assert "is_current_page" in navigation_links["Timing"]
        assert "Status" in navigation_links
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links

    def test_status_view_has_info_timing_status_summary_links(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action.target_completion_date = None
        self.strategic_action.save()
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" in navigation_links
        assert "not_a_link" not in navigation_links["Timing"]
        assert "Status" in navigation_links
        assert "is_current_page" in navigation_links["Status"]
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links

    def test_summary_view_has_info_timing_status_summary_links(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action.target_completion_date = None
        self.strategic_action.save()
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" in navigation_links
        assert "not_a_link" not in navigation_links["Timing"]
        assert "Status" in navigation_links
        assert "not_a_link" not in navigation_links["Status"]
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links
        assert "is_current_page" in navigation_links["Summary"]


class TestWithCompletionDateMonthlyUpdateNavigationItems:
    def setup_method(self):
        self.supply_chain = SupplyChainFactory()
        self.strategic_action = StrategicActionFactory(supply_chain=self.supply_chain)
        self.strategic_action_update = StrategicActionUpdateFactory(
            strategic_action=self.strategic_action,
            supply_chain=self.strategic_action.supply_chain,
        )

    def test_info_view_has_info_status_summary_links_if_completion_date_unchanged(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "is_current_page" in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links

    def test_info_view_has_info_status_revisedtiming_summary_links_if_completion_date_changed(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action_update.changed_value_for_target_completion_date = date(
            year=2021, month=12, day=25
        )
        self.strategic_action_update.save()

        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "is_current_page" in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "RevisedTiming" in navigation_links
        assert "Summary" in navigation_links

    def test_info_view_has_info_status_revisedtiming_summary_links_if_is_ongoing_changed(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action_update.changed_value_for_is_ongoing = True
        self.strategic_action_update.save()

        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "is_current_page" in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "RevisedTiming" in navigation_links
        assert "Summary" in navigation_links

    def test_status_view_has_info_status_summary_links_if_completion_date_unchanged(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "is_current_page" in navigation_links["Status"]
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links

    def test_status_view_has_info_status_revisedtiming_summary_links_if_completion_date_changed(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action_update.changed_value_for_target_completion_date = date(
            year=2021, month=12, day=25
        )
        self.strategic_action_update.save()

        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "is_current_page" in navigation_links["Status"]
        assert "RevisedTiming" in navigation_links
        assert "Summary" in navigation_links

    def test_status_view_has_info_status_revisedtiming_summary_links_if_is_ongoing_changed(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action_update.changed_value_for_is_ongoing = True
        self.strategic_action_update.save()

        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "is_current_page" in navigation_links["Status"]
        assert "RevisedTiming" in navigation_links
        assert "Summary" in navigation_links

    def test_revised_timing_view_has_info_status_revisedtiming_summary_links(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-revised-timing-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "not_a_link" not in navigation_links["Status"]
        assert "RevisedTiming" in navigation_links
        assert "is_current_page" in navigation_links["RevisedTiming"]
        assert "Summary" in navigation_links

    def test_summary_view_has_info_status_summary_links_if_completion_date_unchanged(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "not_a_link" not in navigation_links["Status"]
        assert "RevisedTiming" not in navigation_links
        assert "Summary" in navigation_links
        assert "is_current_page" in navigation_links["Summary"]

    def test_summary_view_has_info_status_revised_timing_summary_links_if_completion_date_changed(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action_update.changed_value_for_target_completion_date = date(
            year=2021, month=12, day=25
        )
        self.strategic_action_update.save()

        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "not_a_link" not in navigation_links["Status"]
        assert "RevisedTiming" in navigation_links
        assert "not_a_link" not in navigation_links["RevisedTiming"]
        assert "Summary" in navigation_links
        assert "is_current_page" in navigation_links["Summary"]

    def test_summary_view_has_info_status_revised_timing_summary_links_if_is_ongoing_changed(
        self, logged_in_client, test_user
    ):
        test_user.gov_department = self.supply_chain.gov_department
        test_user.save()
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )

        self.strategic_action_update.changed_value_for_is_ongoing = True
        self.strategic_action_update.save()

        response = logged_in_client.get(url)

        navigation_links = response.context_data["navigation_links"]
        assert "Info" in navigation_links
        assert "not_a_link" not in navigation_links["Info"]
        assert "Timing" not in navigation_links
        assert "Status" in navigation_links
        assert "not_a_link" not in navigation_links["Status"]
        assert "RevisedTiming" in navigation_links
        assert "not_a_link" not in navigation_links["RevisedTiming"]
        assert "Summary" in navigation_links
        assert "is_current_page" in navigation_links["Summary"]


class TestMonthlyUpdateFormPagesPermissions:
    def setup_method(self):
        self.supply_chain = SupplyChainFactory()
        self.strategic_action = StrategicActionFactory(supply_chain=self.supply_chain)
        self.strategic_action_update = StrategicActionUpdateFactory(
            strategic_action=self.strategic_action,
            supply_chain=self.strategic_action.supply_chain,
        )

    def ensure_user_lacks_permissions(self, test_user, supply_chain):
        # need to be sure the user is from the wrong department for the supply chain
        department_pk = supply_chain.gov_department.pk
        wrong_department = (
            GovDepartment.objects.exclude(pk=department_pk).order_by("?").first()
        )
        test_user.gov_department = wrong_department
        test_user.save()

    def test_monthly_update_create_view_requires_user_permissions(
        self, logged_in_client, test_user
    ):
        url = reverse(
            "monthly-update-create",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
            },
        )
        client = logged_in_client
        self.ensure_user_lacks_permissions(
            test_user=test_user, supply_chain=self.supply_chain
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_monthly_update_info_view_requires_user_permissions(
        self, logged_in_client, test_user
    ):
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        client = logged_in_client
        self.ensure_user_lacks_permissions(
            test_user=test_user, supply_chain=self.supply_chain
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_monthly_update_timing_view_requires_user_permissions(
        self, logged_in_client, test_user
    ):
        url = reverse(
            "monthly-update-timing-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        client = logged_in_client
        self.ensure_user_lacks_permissions(
            test_user=test_user, supply_chain=self.supply_chain
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_monthly_update_status_view_requires_user_permissions(
        self, logged_in_client, test_user
    ):
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        client = logged_in_client
        self.ensure_user_lacks_permissions(
            test_user=test_user, supply_chain=self.supply_chain
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_monthly_update_revised_timing_view_requires_user_permissions(
        self, logged_in_client, test_user
    ):
        url = reverse(
            "monthly-update-revised-timing-edit",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        client = logged_in_client
        self.ensure_user_lacks_permissions(
            test_user=test_user, supply_chain=self.supply_chain
        )
        response = client.get(url)
        assert response.status_code == 403

    def test_monthly_update_summary_view_requires_user_permissions(
        self, logged_in_client, test_user
    ):
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": self.strategic_action.supply_chain.slug,
                "action_slug": self.strategic_action.slug,
                "update_slug": self.strategic_action_update.slug,
            },
        )
        client = logged_in_client
        self.ensure_user_lacks_permissions(
            test_user=test_user, supply_chain=self.supply_chain
        )
        response = client.get(url)
        assert response.status_code == 403


class TestMonthlyUpdateInfoCreateView:
    def test_new_strategic_action_has_user_set(self, logged_in_client, test_user):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        url = reverse(
            "monthly-update-create",
            kwargs={
                "supply_chain_slug": supply_chain.slug,
                "action_slug": strategic_action.slug,
            },
        )
        test_user.gov_department = supply_chain.gov_department
        test_user.save()
        logged_in_client.get(url)
        strategic_action_update = strategic_action.monthly_updates.order_by(
            "-last_modified"
        ).first()
        assert strategic_action_update.user == test_user
