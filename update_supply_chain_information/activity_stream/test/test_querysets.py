import datetime
import json
import time
from datetime import date
from itertools import islice
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from pytz import UTC

from accounts.models import GovDepartment
from accounts.test.factories import UserFactory
from activity_stream.models import ActivityStreamQuerySetWrapper
from activity_stream.viewsets import ActivityStreamViewSet
from supply_chains.models import StrategicAction, StrategicActionQuerySet, SupplyChain
from supply_chains.test.factories import (
    SupplyChainFactory,
    StrategicActionFactory,
    StrategicActionUpdateFactory,
)

pytestmark = pytest.mark.django_db


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
def start_time(item_count):
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
def strategic_action_queryset(last_modified_times) -> StrategicActionQuerySet:
    supply_chain = SupplyChainFactory()
    with mock.patch("django.utils.timezone.now") as mock_now:
        for last_modified in last_modified_times:
            mock_now.return_value = last_modified
            StrategicActionFactory(supply_chain=supply_chain)
    return StrategicAction.objects.all()


class TestActivityStreamQuerySetMixin:
    def test_activity_stream_queryset_includes_last_modified(
        self, strategic_action_queryset, last_modified_times
    ):
        queryset = strategic_action_queryset.for_activity_stream().order_by(
            "last_modified"
        )
        instance = queryset.last()
        assert "last_modified" in instance
        assert instance["last_modified"] == last_modified_times[-1]

    def test_activity_stream_queryset_includes_foreign_key_field_information(
        self, strategic_action_queryset
    ):
        instance = strategic_action_queryset.for_activity_stream().first()
        assert "foreign_keys" in instance
        foreign_keys = instance["foreign_keys"]["keys"]
        assert "supply_chain" == foreign_keys[0][0]
        assert "SupplyChain" == foreign_keys[0][1]

    def test_activity_stream_queryset_includes_object_type(
        self, strategic_action_queryset
    ):
        instance = strategic_action_queryset.for_activity_stream().first()
        assert "object_type" in instance
        assert "StrategicAction" == instance["object_type"]

    def test_activity_stream_queryset_includes_json_object(
        self, strategic_action_queryset
    ):
        instance = strategic_action_queryset.for_activity_stream().first()
        assert "json" in instance
        assert isinstance(instance["json"], dict)

    def test_activity_stream_queryset_json_object_includes_expected_fields(
        self, strategic_action_queryset
    ):
        expected_keys = [
            "id",
            "name",
            "slug",
            "impact",
            "category",
            "is_ongoing",
            "start_date",
            "description",
            "is_archived",
            "supply_chain",
            "archived_date",
            "last_modified",
            "archived_reason",
            "geographic_scope",
            "other_dependencies",
            "target_completion_date",
            "supporting_organisations",
            "specific_related_products",
        ]
        instance = strategic_action_queryset.for_activity_stream().first()
        object = instance["json"]
        for key in expected_keys:
            assert key in object

    def test_queryset_modified_after(self, strategic_action_queryset):
        count = strategic_action_queryset.count()
        halfway = count // 2
        halfway_last_modified = strategic_action_queryset.order_by("last_modified")[
            halfway - 1
        ].last_modified
        queryset_modified_after = strategic_action_queryset.modified_after(
            halfway_last_modified
        )
        assert queryset_modified_after.count() == count - halfway


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
    supply_chain = None
    strategic_action = None
    gov_department: GovDepartment = GovDepartment.objects.first()
    user = UserFactory(gov_department=gov_department)
    with mock.patch("django.utils.timezone.now") as mock_now:
        for i, last_modified in enumerate(bit_of_everything_last_modified_times):
            mock_now.return_value = last_modified
            if i % 8 == 0:
                supply_chain = SupplyChainFactory(gov_department=gov_department)
                continue
            if i % 5 == 1:
                strategic_action = StrategicActionFactory(supply_chain=supply_chain)
                continue
            StrategicActionUpdateFactory(
                supply_chain=supply_chain, strategic_action=strategic_action, user=user
            )


@pytest.fixture(scope="function")
def wrapped_union_queryset(bit_of_everything_queryset):
    # we don't directly use the queryset, but referencing it as a parameter ensures it exists
    # otherwise the union of all querysets would only contain a GovDepartment and a User :-)
    return ActivityStreamQuerySetWrapper()


class TestActivityStreamQuerySetWrapper:
    def test_queryset_wrapper_delegates_slicing(self, wrapped_union_queryset):
        queryset_slice = wrapped_union_queryset[1:5]
        assert len(queryset_slice) == 4

    def test_queryset_wrapper_delegates_count(
        self, wrapped_union_queryset, bit_of_everything_item_count
    ):
        count = wrapped_union_queryset.count()
        # contents of queryset + 1 GovDepartment + 1 User
        assert count == bit_of_everything_item_count + 2

    def test_queryset_wrapper_orders_queryset(self, wrapped_union_queryset):
        last_modified_values = [
            item["last_modified"]
            for item in wrapped_union_queryset.order_by("last_modified")
        ]
        for earlier, later in zip(last_modified_values[:-1], last_modified_values[1:]):
            assert earlier <= later

    def test_union_queryset_can_filter(
        self, wrapped_union_queryset, bit_of_everything_item_count
    ):
        total_count = wrapped_union_queryset.count()
        ordered_queryset = wrapped_union_queryset.order_by("last_modified")
        date_from_index = bit_of_everything_item_count // 2
        date_from = ordered_queryset[date_from_index - 1]["last_modified"]
        filtered_queryset = wrapped_union_queryset.filter(last_modified__gt=date_from)
        assert filtered_queryset.count() == total_count - date_from_index

    def test_ordered_filtered_union_queryset_was_not_evaluated(
        self, bit_of_everything_last_modified_times
    ):
        # The entire point of all this queryset wrapper stuff is to ensure
        # the queryset isn't evaluated until after it's been ordered and filtered.
        # So let's just check, to be on the safe side :-)
        # N.B. The order of operations here is specifically the same as in DRF CursorPagination,
        # as that's the thing we want to get working. It's not good to be depending
        # on such implementation details, but in theory the technique used in the wrapper is resilient
        # to any change within DRF.
        date_from = bit_of_everything_last_modified_times[7]
        ordered_filtered_union_queryset = (
            ActivityStreamQuerySetWrapper()
            .order_by("last_modified")
            .filter(last_modified__gt=date_from)
        )
        # Another implementation detail: a queryset's `_result_cache` is populated when it's evaluated
        assert ordered_filtered_union_queryset._queryset._result_cache is None
