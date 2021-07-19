import pytest

from activity_stream.models import ActivityStreamQuerySetWrapper
from supply_chains.models import StrategicActionUpdate

pytestmark = pytest.mark.django_db


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

    def test_strategic_action_update_activity_stream_queryset_includes_only_submitted(
        self, strategic_action_update_queryset
    ):
        submitted_count = 0
        update: StrategicActionUpdate
        for index, update in enumerate(strategic_action_update_queryset):
            if index % 3:
                update.status = StrategicActionUpdate.Status.SUBMITTED
                submitted_count += 1
            else:
                update.status = StrategicActionUpdate.Status.IN_PROGRESS
            update.save()

        updates_for_feed = StrategicActionUpdate.objects.for_activity_stream()
        assert updates_for_feed.count() == submitted_count


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
