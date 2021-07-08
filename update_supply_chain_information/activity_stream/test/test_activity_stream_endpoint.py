from unittest import mock

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestActivityStreamEndpoint:
    def test_full_page_has_next_link(
        self, wrapped_union_queryset, test_client_with_token
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            endpoint = reverse("activity-stream-list")
            response = test_client_with_token.get(endpoint)
            json = response.json()
            assert "next" in json

    def test_full_page_has_all_objects(
        self, wrapped_union_queryset, test_client_with_token
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            endpoint = reverse("activity-stream-list")
            response = test_client_with_token.get(endpoint)
            json = response.json()
            assert len(json["orderedItems"]) == page_length

    def test_last_page_has_no_next_link(
        self, wrapped_union_queryset, test_client_with_token
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            endpoint = reverse("activity-stream-list")
            response = test_client_with_token.get(endpoint)
            json = response.json()
            next_page_link = json["next"]
            response = test_client_with_token.get(next_page_link)
            json = response.json()
            assert "next" not in json

    def test_last_page_has_no_objects(
        self, wrapped_union_queryset, test_client_with_token
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            endpoint = reverse("activity-stream-list")
            response = test_client_with_token.get(endpoint)
            json = response.json()
            next_page_link = json["next"]
            response = test_client_with_token.get(next_page_link)
            json = response.json()
            assert len(json["orderedItems"]) == 0

    def test_multiple_pages_have_items_in_order_of_last_modified_date_ascending(
        self,
        wrapped_union_queryset,
        test_client_with_token,
    ):
        page_length = (
            wrapped_union_queryset.count() // 3
        )  # ensure things are spread over several pages
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            results = []
            endpoint = reverse("activity-stream-list")
            while endpoint:
                response = test_client_with_token.get(endpoint)
                json = response.json()
                items = json["orderedItems"]
                results += [
                    earlier["object"]["last_modified"]
                    <= later["object"]["last_modified"]
                    for earlier, later in zip(items[:-1], items[1:])
                ]
                endpoint = json.get("next", None)
            assert all(results)
