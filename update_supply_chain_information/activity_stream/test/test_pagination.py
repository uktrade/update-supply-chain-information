from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from rest_framework.request import Request

from activity_stream.models import ActivityStreamQuerySetWrapper
from activity_stream.pagination import ActivityStreamCursorPagination
from supply_chains.models import SupplyChain

pytestmark = pytest.mark.django_db


class TestActivityStreamCursorPagination:
    def test_last_page_has_next_page(self, wrapped_union_queryset, rf):
        """
        Ensure the pagination links to a next page,
        even when that page will be empty as the queryset has been exhausted on this page.
        """
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            request = rf.get(reverse("activity-stream-list"))
            drf_request = Request(request)
            pagination = ActivityStreamCursorPagination()
            pagination.paginate_queryset(wrapped_union_queryset, drf_request)
            assert pagination.has_next

    def test_modified_item_appears_on_next_page(
        self, wrapped_union_queryset, rf, bit_of_everything_last_modified_times
    ):
        """
        Ensure the pagination links to a next page,
        even when that page will be empty as the queryset has been exhausted on this page.
        """
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            request = rf.get(reverse("activity-stream-list"))
            drf_request = Request(request)
            pagination = ActivityStreamCursorPagination()
            pagination.paginate_queryset(wrapped_union_queryset, drf_request)
            # Change a supply chain so its last_modified date is later
            # than the last_modified date of the last item on the page we've just built
            supply_chain = SupplyChain.objects.order_by("last_modified").first()
            expected_end_of_name = " modified"
            supply_chain.name = supply_chain.name + expected_end_of_name
            # Get a last_modified datetime later than the end of the existing queryset
            latest_timestamp = bit_of_everything_last_modified_times[-1]
            offset = relativedelta(months=1)
            new_timestamp = latest_timestamp + offset
            with mock.patch("django.utils.timezone.now") as mock_now:
                mock_now.return_value = new_timestamp
                supply_chain.save()
            # Ensure we have an updated queryset
            updated_queryset = ActivityStreamQuerySetWrapper()
            next_link = pagination.get_next_link()
            request = rf.get(next_link)
            drf_request = Request(request)
            # Ensure we start with a clean slate to prevent any previous pagination state affecting things
            pagination = ActivityStreamCursorPagination()
            page_items = pagination.paginate_queryset(updated_queryset, drf_request)
            # Pagination should now link to a new empty last page
            assert pagination.has_next
            assert len(page_items) == 1
            name: str = page_items[0]["json"]["name"]
            assert name.endswith(expected_end_of_name)
            assert page_items[0]["last_modified"] == new_timestamp

    def test_pagination_has_no_next_page_after_empty_last_page(
        self, wrapped_union_queryset, rf
    ):
        """
        Make the page length the size of the queryset, get the first page, get the next page, check it has no next link.
        Seems inefficient to paginate twice, but I couldn't work out an easier way without spending ages
        analysing how DRF pagination's internal mechanisms work; and when I looked at its tests for ideas,
        it turned out that's what they do for similar test cases.
        """
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            request = rf.get(reverse("activity-stream-list"))
            drf_request = Request(request)
            pagination = ActivityStreamCursorPagination()
            pagination.paginate_queryset(wrapped_union_queryset, drf_request)
            next_link = pagination.get_next_link()
            request = rf.get(next_link)
            drf_request = Request(request)
            # ensure we start with a clean slate to prevent any previous pagination state affecting things
            pagination = ActivityStreamCursorPagination()
            page_items = pagination.paginate_queryset(
                wrapped_union_queryset, drf_request
            )
            assert not pagination.has_next
            assert not page_items

    def test_pagination_has_no_next_page_when_queryset_is_empty(
        self, empty_queryset, rf
    ):
        """
        Unlikely to happen but anything's possible,
        so make sure we get an empty last page even if it's the first page
        as otherwise Activity Stream might get confused
        """
        page_length = 100
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            request = rf.get(reverse("activity-stream-list"))
            drf_request = Request(request)
            pagination = ActivityStreamCursorPagination()
            page_items = pagination.paginate_queryset(empty_queryset, drf_request)
            assert not pagination.has_next
            assert not page_items

    def test_paginated_response_has_next_link_on_last_page_of_content(
        self, wrapped_union_queryset, rf
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            request = rf.get(reverse("activity-stream-list"))
            drf_request = Request(request)
            pagination = ActivityStreamCursorPagination()
            data = pagination.paginate_queryset(wrapped_union_queryset, drf_request)
            paginated_response = pagination.get_paginated_response(data)
            assert "next" in paginated_response.data

    def test_paginated_response_has_no_next_link_on_empty_page(
        self, empty_queryset, rf
    ):
        page_length = 100
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            request = rf.get(reverse("activity-stream-list"))
            drf_request = Request(request)
            pagination = ActivityStreamCursorPagination()
            data = pagination.paginate_queryset(empty_queryset, drf_request)
            paginated_response = pagination.get_paginated_response(data)
            assert "next" not in paginated_response.data
