from unittest import mock
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import GovDepartment
from accounts.test.factories import GovDepartmentFactory
from supply_chains.forms import YesNoChoices, ApproximateTimings
from supply_chains.models import StrategicAction, StrategicActionUpdate, RAGRating
from supply_chains.test.factories import (
    StrategicActionUpdateFactory,
)
from supply_chains.models import SupplyChain
from supply_chains.test.factories import StrategicActionFactory, SupplyChainFactory

pytestmark = pytest.mark.django_db

# Strategic Action fixtures in various configurations


@pytest.fixture
def strategic_action_without_timing():
    supply_chain = SupplyChainFactory()
    strategic_action: StrategicAction = StrategicActionFactory(
        supply_chain=supply_chain, target_completion_date=None, is_ongoing=False
    )
    return strategic_action


@pytest.fixture
def strategic_action_with_completion_date():
    supply_chain = SupplyChainFactory()
    strategic_action: StrategicAction = StrategicActionFactory(
        supply_chain=supply_chain,
        target_completion_date=date.today() + relativedelta(months=2),
        is_ongoing=False,
    )
    return strategic_action


@pytest.fixture
def strategic_action_with_is_ongoing():
    supply_chain = SupplyChainFactory()
    strategic_action: StrategicAction = StrategicActionFactory(
        supply_chain=supply_chain, target_completion_date=None, is_ongoing=True
    )
    return strategic_action


# Strategic Action Update fixtures in various configurations


@pytest.fixture
def strategic_action_update_info_timing_status_incomplete(
    strategic_action_without_timing,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        content="",
        changed_value_for_target_completion_date=None,
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=None,
        reason_for_delays="",
        reason_for_completion_date_change="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_timing_status_incomplete(strategic_action_without_timing):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=None,
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=None,
        reason_for_delays="",
        reason_for_completion_date_change="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_status_incomplete_with_changed_completion_date(
    strategic_action_without_timing,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=None,
        reason_for_delays="",
        reason_for_completion_date_change="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_status_incomplete_with_changed_is_ongoing(
    strategic_action_without_timing,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=None,
        changed_value_for_is_ongoing=True,
        implementation_rag_rating=None,
        reason_for_delays="",
        reason_for_completion_date_change="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_without_action_status(strategic_action_without_timing):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=None,
        reason_for_delays="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_with_action_status_green(strategic_action_without_timing):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=RAGRating.GREEN,
        reason_for_delays="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_with_action_status_amber(strategic_action_without_timing):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=RAGRating.AMBER,
        reason_for_delays="Foo",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_with_action_status_red(strategic_action_without_timing):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=RAGRating.RED,
        reason_for_delays="Foo",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_complete_with_changed_completion_date(
    strategic_action_without_timing,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=RAGRating.GREEN,
        reason_for_delays="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_complete_with_changed_is_ongoing(
    strategic_action_without_timing,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_without_timing,
        supply_chain=strategic_action_without_timing.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=None,
        changed_value_for_is_ongoing=True,
        implementation_rag_rating=RAGRating.GREEN,
        reason_for_delays="",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_complete_with_revised_completion_date(
    strategic_action_with_completion_date,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_with_completion_date,
        supply_chain=strategic_action_with_completion_date.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=date.today() + relativedelta(months=1),
        changed_value_for_is_ongoing=False,
        implementation_rag_rating=RAGRating.GREEN,
        reason_for_delays="",
        reason_for_completion_date_change="Foo",
    )
    return strategic_action_update


@pytest.fixture
def strategic_action_update_complete_with_revised_is_ongoing(
    strategic_action_with_completion_date,
):
    strategic_action_update = StrategicActionUpdateFactory(
        strategic_action=strategic_action_with_completion_date,
        supply_chain=strategic_action_with_completion_date.supply_chain,
        content="Foo",
        changed_value_for_target_completion_date=None,
        changed_value_for_is_ongoing=True,
        implementation_rag_rating=RAGRating.GREEN,
        reason_for_delays="",
        reason_for_completion_date_change="Foo",
    )
    return strategic_action_update


class TestNoCompletionDateInfoPageNavigationLinks:
    def info_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_info_view_not_linked_to_self_when_not_completed(
        self,
        strategic_action_update_info_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_info_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_info_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        info_item = navigation_items["Info"]
        assert "not_a_link" in info_item

    def test_update_info_view_not_linked_to_self_when_completed(
        self,
        strategic_action_update_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        info_item = navigation_items["Info"]
        assert "not_a_link" in info_item

    def test_update_info_view_has_timing_not_linked_when_not_completed(
        self,
        strategic_action_update_info_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_info_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_info_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["Timing"]
        assert "not_a_link" in timing_item

    def test_update_info_view_has_timing_linked_when_new_completion_date(
        self,
        strategic_action_update_status_incomplete_with_changed_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_status_incomplete_with_changed_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(
                strategic_action_update_status_incomplete_with_changed_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["Timing"]
        assert "not_a_link" not in timing_item

    def test_update_info_view_has_timing_linked_when_new_is_ongoing(
        self,
        strategic_action_update_status_incomplete_with_changed_is_ongoing,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_status_incomplete_with_changed_is_ongoing.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(
                strategic_action_update_status_incomplete_with_changed_is_ongoing
            )
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["Timing"]
        assert "not_a_link" not in timing_item

    def test_update_info_view_has_status_not_linked_when_not_completed(
        self,
        strategic_action_update_status_incomplete_with_changed_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_status_incomplete_with_changed_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(
                strategic_action_update_status_incomplete_with_changed_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" in status_item

    def test_update_info_view_has_status_linked_when_green(
        self,
        strategic_action_update_with_action_status_green,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_with_action_status_green.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_with_action_status_green)
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" not in status_item

    def test_update_info_view_has_status_linked_when_amber(
        self,
        strategic_action_update_with_action_status_amber,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_with_action_status_amber.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_with_action_status_amber)
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" not in status_item

    def test_update_info_view_has_status_linked_when_red(
        self,
        strategic_action_update_with_action_status_red,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_with_action_status_red.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_with_action_status_red)
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" not in status_item

    def test_update_info_view_has_summary_not_linked_when_info_timing_status_incomplete(
        self,
        strategic_action_update_info_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_info_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_info_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" in summary_item

    def test_update_info_view_has_summary_not_linked_when_timing_status_incomplete(
        self,
        strategic_action_update_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" in summary_item

    def test_update_info_view_has_summary_not_linked_with_new_completion_date_when_status_incomplete(
        self,
        strategic_action_update_status_incomplete_with_changed_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_status_incomplete_with_changed_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(
                strategic_action_update_status_incomplete_with_changed_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" in summary_item

    def test_update_info_view_has_summary_not_linked_with_new_is_ongoing_when_status_incomplete(
        self,
        strategic_action_update_status_incomplete_with_changed_is_ongoing,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_status_incomplete_with_changed_is_ongoing.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(
                strategic_action_update_status_incomplete_with_changed_is_ongoing
            )
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" in summary_item

    def test_update_info_view_has_summary_linked_when_all_complete_with_new_completion_date(
        self,
        strategic_action_update_complete_with_changed_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_changed_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_complete_with_changed_completion_date)
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" not in summary_item

    def test_update_info_view_has_summary_linked_when_all_complete_with_new_is_ongoing(
        self,
        strategic_action_update_complete_with_changed_is_ongoing,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_changed_is_ongoing.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_complete_with_changed_is_ongoing)
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" not in summary_item


class TestNoCompletionDateTimingPageNavigationLinks:
    def timing_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-timing-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_timing_view_not_linked_to_self_when_not_completed(
        self,
        strategic_action_update_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.timing_url(strategic_action_update_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["Timing"]
        assert "not_a_link" in timing_item

    def test_update_timing_view_not_linked_to_self_when_completed(
        self,
        strategic_action_update_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.timing_url(strategic_action_update_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["Timing"]
        assert "not_a_link" in timing_item

    def test_update_timing_view_has_info_view_linked(
        self,
        strategic_action_update_info_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_info_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.timing_url(strategic_action_update_info_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        info_item = navigation_items["Info"]
        assert "not_a_link" not in info_item


class TestNoCompletionDateStatusPageNavigationLinks:
    def status_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_status_view_not_linked_to_self_when_not_completed(
        self,
        strategic_action_update_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.status_url(strategic_action_update_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" in status_item

    def test_update_status_view_not_linked_to_self_when_completed(
        self,
        strategic_action_update_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.status_url(strategic_action_update_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" in status_item

    def test_update_status_view_has_timing_view_linked(
        self,
        strategic_action_update_info_timing_status_incomplete,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_info_timing_status_incomplete.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.status_url(strategic_action_update_info_timing_status_incomplete)
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["Timing"]
        assert "not_a_link" not in timing_item


class TestNoCompletionDateSummaryPageNavigationLinks:
    def summary_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_summary_view_not_linked_to_self_when_completed(
        self,
        strategic_action_update_complete_with_changed_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_changed_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.summary_url(
                strategic_action_update_complete_with_changed_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        summary_item = navigation_items["Summary"]
        assert "not_a_link" in summary_item

    def test_update_summary_view_has_status_view_linked(
        self,
        strategic_action_update_complete_with_changed_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_changed_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.summary_url(
                strategic_action_update_complete_with_changed_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["Status"]
        assert "not_a_link" not in status_item


class TestWithCompletionDateInfoPageNavigationLinks:
    def info_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_info_view_has_revised_timing_linked(
        self,
        strategic_action_update_complete_with_revised_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_revised_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.info_url(strategic_action_update_complete_with_revised_completion_date)
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["RevisedTiming"]
        assert "not_a_link" not in status_item


class TestWithCompletionDateTimingPageNavigationLinks:
    def timing_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-timing-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_info_view_has_revised_timing_linked(
        self,
        strategic_action_update_complete_with_revised_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_revised_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.timing_url(
                strategic_action_update_complete_with_revised_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["RevisedTiming"]
        assert "not_a_link" not in status_item


class TestWithCompletionDateStatusPageNavigationLinks:
    def status_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_status_view_has_revised_timing_linked(
        self,
        strategic_action_update_complete_with_revised_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_revised_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.status_url(
                strategic_action_update_complete_with_revised_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["RevisedTiming"]
        assert "not_a_link" not in status_item


class TestWithCompletionDateRevisedTimingPageNavigationLinks:
    def revised_timing_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-revised-timing-edit",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_revised_timing_view_not_linked_to_self_when_completed(
        self,
        strategic_action_update_complete_with_revised_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_revised_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.revised_timing_url(
                strategic_action_update_complete_with_revised_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        timing_item = navigation_items["RevisedTiming"]
        assert "not_a_link" in timing_item


class TestWithCompletionDateSummaryPageNavigationLinks:
    def summary_url(self, strategic_action_update: StrategicActionUpdate):
        url = reverse(
            "monthly-update-summary",
            kwargs={
                "supply_chain_slug": strategic_action_update.supply_chain.slug,
                "action_slug": strategic_action_update.strategic_action.slug,
                "update_slug": strategic_action_update.slug,
            },
        )
        return url

    def test_update_summary_view_has_revised_timing_linked(
        self,
        strategic_action_update_complete_with_revised_completion_date,
        logged_in_client,
        test_user,
    ):
        test_user.gov_department = (
            strategic_action_update_complete_with_revised_completion_date.supply_chain.gov_department
        )
        test_user.save()

        response = logged_in_client.get(
            self.summary_url(
                strategic_action_update_complete_with_revised_completion_date
            )
        )
        navigation_items = response.context_data["navigation_links"]

        status_item = navigation_items["RevisedTiming"]
        assert "not_a_link" not in status_item
