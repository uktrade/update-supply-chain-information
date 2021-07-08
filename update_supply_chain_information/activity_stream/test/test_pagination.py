from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.request import Request

from activity_stream.pagination import ActivityStreamCursorPagination

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
