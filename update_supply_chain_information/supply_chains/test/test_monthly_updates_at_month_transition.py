from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

import pytest
from django.http import HttpRequest
from django.template.response import TemplateResponse

from supply_chains.models import (
    StrategicAction,
    SupplyChain,
    StrategicActionUpdate,
)
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
)
from accounts.models import User

from supply_chains.views import SCTaskListView

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.first()


@pytest.fixture
def submission_date() -> date:
    return date(year=2021, month=5, day=27)


@pytest.fixture
def supply_chain(submission_date: date) -> SupplyChain:
    supply_chain: SupplyChain = SupplyChainFactory(last_submission_date=submission_date)
    strategic_action = StrategicActionFactory(supply_chain=supply_chain)
    strategic_action_update: StrategicActionUpdate = StrategicActionUpdateFactory(
        status=StrategicActionUpdate.Status.SUBMITTED,
        supply_chain=supply_chain,
        strategic_action=strategic_action,
        submission_date=submission_date,
    )
    return supply_chain


@pytest.fixture
def http_request(user) -> HttpRequest:
    request = HttpRequest()
    request.method = "GET"
    request.user = user
    return request


@pytest.fixture
def view(supply_chain) -> dict:
    view = SCTaskListView.as_view()
    return {"supply_chain_slug": supply_chain.slug}


class TestMonthlyUpdateAtMonthTransition:
    def test_strategic_action_update_submitted(self, supply_chain: SupplyChain):
        strategic_action: StrategicAction = supply_chain.strategic_actions.first()
        strategic_action_update: StrategicActionUpdate = (
            strategic_action.monthly_updates.first()
        )
        assert strategic_action_update.status == StrategicActionUpdate.Status.SUBMITTED

    # def test_task_list_view_shows_new_update_required(self, http_request, view):
    #     response: TemplateResponse = view(http_request, view_kwargs)
    #     context = response.context_data
    #     responding_view = context['view']
    #     assert view is not None
