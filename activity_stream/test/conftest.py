import datetime
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet
from django.urls import reverse
from pytz import UTC

from accounts.models import GovDepartment
from accounts.test.factories import UserFactory
from activity_stream.models import ActivityStreamQuerySetWrapper
from activity_stream.test.util.hawk import get_hawk_header
from supply_chains.models import (
    StrategicAction,
    StrategicActionQuerySet,
    StrategicActionUpdate,
    ScenarioAssessment,
    ScenarioAssessmentQuerySet,
)
from supply_chains.test.factories import (
    StrategicActionUpdateFactory,
    SupplyChainFactory,
    StrategicActionFactory,
    ScenarioAssessmentFactory,
)


@pytest.fixture()
def supply_chain():
    return SupplyChainFactory()


@pytest.fixture(scope="session")
def item_count():
    return 12


@pytest.fixture(scope="session")
def halfway_item_index(item_count):
    return item_count // 2


@pytest.fixture(scope="session")
def start_time():
    return datetime.datetime(year=2022, month=12, day=25, hour=11, tzinfo=UTC)


@pytest.fixture(scope="session")
def time_delta():
    # Let's chuck some primes in there, like cicadas.
    # Not at all necessary, as a millisecond would do for the test itself;
    # but it makes the differences more obvious if looking at the tests in the debugger :-)
    return relativedelta(days=1, hours=7, minutes=17)


@pytest.fixture(scope="session")
def last_modified_times(start_time, time_delta, item_count):
    times = [start_time + (time_delta * i) for i in range(0, item_count)]
    return times


@pytest.fixture(scope="function")
def strategic_action_queryset(
    supply_chain, last_modified_times
) -> StrategicActionQuerySet:
    with mock.patch("django.utils.timezone.now") as mock_now:
        for last_modified in last_modified_times:
            mock_now.return_value = last_modified
            StrategicActionFactory(supply_chain=supply_chain)
    return StrategicAction.objects.all()


@pytest.fixture(scope="function")
def scenario_assessment_queryset(last_modified_times) -> ScenarioAssessmentQuerySet:
    supply_chain = SupplyChainFactory(name="SA OneToOne Test Supply Chain")
    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = last_modified_times[0]
        ScenarioAssessmentFactory(supply_chain=supply_chain)
    return ScenarioAssessment.objects.all()


@pytest.fixture()
def strategic_action_update_queryset(strategic_action_queryset, last_modified_times):
    for strategic_action in strategic_action_queryset:
        StrategicActionUpdateFactory(
            strategic_action=strategic_action,
            supply_chain=strategic_action.supply_chain,
        )
    return StrategicActionUpdate.objects.all()


@pytest.fixture()
def empty_queryset() -> QuerySet:
    return ActivityStreamQuerySetWrapper().none()


@pytest.fixture(scope="session")
def bit_of_everything_item_count():
    return 23


@pytest.fixture(scope="function")
def bit_of_everything_last_modified_times(
    start_time, time_delta, bit_of_everything_item_count
):
    times = [
        start_time + (time_delta * i) for i in range(0, bit_of_everything_item_count)
    ]
    return times


@pytest.fixture(scope="function")
def bit_of_everything_queryset(
    bit_of_everything_item_count, bit_of_everything_last_modified_times
):
    """
    Generate a bunch of SCs, SA, and SAUs so we can be sure there's a good mix for the union queryset.
    Doing them this rather odd way helps check that the ordering works as expected
    by interleaving the last_modified values among the different models,
    such that simply concatenating the instances from each queryset would not be ordered by last_modified.
    To get an idea of what comes out, run the following at the console:
    ['sc' if i % 8 == 0 else 'sa' if i % 4 == 1 else 'sau' for i in range(0, 23)]
    """
    supply_chain_in_use = None
    strategic_action_in_use = None
    gov_department: GovDepartment = GovDepartment.objects.first()
    user = UserFactory(gov_department=gov_department)
    with mock.patch("django.utils.timezone.now") as mock_now:
        for i, last_modified in enumerate(bit_of_everything_last_modified_times):
            mock_now.return_value = last_modified
            if i % 8 == 0:
                supply_chain_in_use = SupplyChainFactory(gov_department=gov_department)
                continue
            if i % 5 == 1:
                strategic_action_in_use = StrategicActionFactory(
                    supply_chain=supply_chain_in_use
                )
                continue
            StrategicActionUpdateFactory(
                supply_chain=supply_chain_in_use,
                strategic_action=strategic_action_in_use,
                user=user,
                status=StrategicActionUpdate.Status.SUBMITTED,
            )


@pytest.fixture(scope="function")
def wrapped_union_queryset(bit_of_everything_queryset) -> ActivityStreamQuerySetWrapper:
    # we don't directly use the queryset, but referencing it as a parameter ensures it exists
    # otherwise the union of all querysets would only contain a GovDepartment :-)
    return ActivityStreamQuerySetWrapper()


@pytest.fixture(scope="session")
def endpoint():
    return f'{reverse("activity-stream-list")}?a=c'


@pytest.fixture()
def hawk_authentication_header(endpoint):
    return get_hawk_header(
        access_key_id="xxx",
        secret_access_key="xxx",
        method="GET",
        host="testserver",
        port="80",
        path=endpoint,
        content_type=b"",
        content=b"",
    )
