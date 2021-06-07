from datetime import date
from unittest import mock

import pytest
from django.http import HttpRequest
from django.template.response import TemplateResponse

from supply_chains.models import (
    StrategicAction,
    SupplyChain,
    StrategicActionUpdate,
    RAGRating,
)
from accounts.models import User, GovDepartment
from supply_chains.views import SCTaskListView

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    dit: GovDepartment = GovDepartment.objects.get(name="DIT")
    user: User
    created: bool
    user, created = User.objects.get_or_create(
        gov_department=dit, email=["foo@digital.dit.gov.uk"]
    )
    return user


@pytest.fixture
def submission_date() -> date:
    return date(year=2021, month=5, day=27)


mock_wrong_last_month_deadline = date(year=2021, month=4, day=30)
mock_correct_last_month_deadline = date(year=2021, month=5, day=28)


@pytest.fixture
def supply_chain(submission_date: date) -> SupplyChain:
    supply_chain: SupplyChain
    created: bool
    supply_chain, created = SupplyChain.objects.get_or_create(
        name="Bananas",
        last_submission_date=submission_date,
        contact_name="Mr. Banana",
        contact_email="banana.email",
        gov_department=GovDepartment.objects.first(),
        vulnerability_status=SupplyChain.StatusRating.LOW,
        vulnerability_status_disagree_reason="",
        risk_severity_status=SupplyChain.StatusRating.LOW,
        risk_severity_status_disagree_reason="",
        archived_date=None,
        is_archived=False,
        archived_reason="",
    )
    strategic_action: StrategicAction
    strategic_action, created = StrategicAction.objects.get_or_create(
        name="Strategic action 1",
        start_date=date(year=2020, month=1, day=24),
        description="Increase banana stockpiles",
        impact="Improved banana availability",
        category=StrategicAction.Category.EXPAND,
        geographic_scope=StrategicAction.GeographicScope.ENGLAND_ONLY,
        supporting_organisations="",
        is_ongoing=False,
        target_completion_date=date(year=2021, month=11, day=27),
        is_archived=False,
        supply_chain=supply_chain,
        other_dependencies="",
        specific_related_products="",
        archived_date=None,
        archived_reason="",
    )
    strategic_action_update: StrategicActionUpdate
    strategic_action_update, created = StrategicActionUpdate.objects.get_or_create(
        status=StrategicActionUpdate.Status.SUBMITTED,
        submission_date=submission_date,
        content="It is going well.",
        implementation_rag_rating=RAGRating.RED,
        reason_for_delays="dfh",
        strategic_action=strategic_action,
        supply_chain=supply_chain,
        user=None,
        date_created=submission_date,
        reason_for_completion_date_change="It's late.",
        changed_value_for_is_ongoing=False,
        changed_value_for_target_completion_date=None,
    )
    strategic_action_update.date_created = submission_date
    strategic_action_update.slug = "05-2021"
    strategic_action_update.save()
    return supply_chain


@pytest.fixture
def http_request(user) -> HttpRequest:
    request = HttpRequest()
    request.method = "GET"
    request.user = user
    return request


class TestMonthlyUpdateAtMonthTransition:
    @mock.patch(
        "supply_chains.views.get_last_working_day_of_previous_month",
        return_value=mock_wrong_last_month_deadline,
    )
    def test_task_list_view_shows_update_submitted_with_wrong_deadline(
        self,
        mocked_deadline,
        supply_chain: SupplyChain,
        http_request,
    ):
        view_kwargs = {"supply_chain_slug": supply_chain.slug}

        view = SCTaskListView.as_view()
        response: TemplateResponse = view(http_request, **view_kwargs)
        context = response.context_data
        responding_view = context["view"]

        mocked_deadline.assert_called_once()
        assert responding_view is not None
        assert responding_view.update_submitted is True
        assert (
            "You have already submitted the monthly update for this supply chain"
            in response.rendered_content
        )
        assert (
            "1 out of 1 actions are not ready to be submitted."
            not in response.rendered_content
        )

    @mock.patch(
        "supply_chains.views.get_last_working_day_of_previous_month",
        return_value=mock_correct_last_month_deadline,
    )
    def test_task_list_view_shows_new_update_required_with_correct_deadline(
        self,
        mocked_deadline,
        supply_chain: SupplyChain,
        http_request,
    ):
        view_kwargs = {"supply_chain_slug": supply_chain.slug}

        view = SCTaskListView.as_view()
        response: TemplateResponse = view(http_request, **view_kwargs)
        context = response.context_data
        responding_view = context["view"]

        mocked_deadline.assert_called_once()
        assert responding_view is not None
        assert responding_view.update_submitted is False
        assert (
            "You have already submitted the monthly update for this supply chain"
            not in response.rendered_content
        )
        assert (
            "1 out of 1 actions are not ready to be submitted."
            in response.rendered_content
        )
