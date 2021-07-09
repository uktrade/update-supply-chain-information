from unittest import mock
from urllib.parse import urlparse

import pytest

from activity_stream.test.util.hawk import get_hawk_header

pytestmark = pytest.mark.django_db


class TestActivityStreamEndpoint:
    def test_full_page_has_next_link(
        self,
        wrapped_union_queryset,
        logged_in_client,
        hawk_authentication_header,
        hawk_credentials_setting,
        endpoint,
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            with mock.patch(
                "django.conf.settings.HAWK_CREDENTIALS", hawk_credentials_setting
            ):
                response = logged_in_client.get(
                    endpoint, HTTP_AUTHORIZATION=hawk_authentication_header
                )
            json = response.json()
            assert "next" in json

    def test_full_page_has_all_objects(
        self,
        wrapped_union_queryset,
        logged_in_client,
        hawk_authentication_header,
        hawk_credentials_setting,
        endpoint,
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            with mock.patch(
                "django.conf.settings.HAWK_CREDENTIALS", hawk_credentials_setting
            ):
                response = logged_in_client.get(
                    endpoint, HTTP_AUTHORIZATION=hawk_authentication_header
                )
            json = response.json()
            assert len(json["orderedItems"]) == page_length

    def test_last_page_has_no_next_link(
        self,
        wrapped_union_queryset,
        logged_in_client,
        hawk_credentials_setting,
        hawk_authentication_header,
        endpoint,
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            with mock.patch(
                "django.conf.settings.HAWK_CREDENTIALS", hawk_credentials_setting
            ):
                response = logged_in_client.get(
                    endpoint, HTTP_AUTHORIZATION=hawk_authentication_header
                )
                json = response.json()
                next_page_link = json["next"]
                hawk_authentication_header = get_hawk_header(
                    access_key_id=hawk_credentials_setting["testsettings"]["id"],
                    secret_access_key=hawk_credentials_setting["testsettings"]["key"],
                    method="GET",
                    host="testserver",
                    port="80",
                    path=next_page_link,
                    content_type=b"",
                    content=b"",
                )
                response = logged_in_client.get(
                    next_page_link, HTTP_AUTHORIZATION=hawk_authentication_header
                )
                json = response.json()
                assert "next" not in json

    def test_last_page_has_no_objects(
        self,
        wrapped_union_queryset,
        logged_in_client,
        hawk_authentication_header,
        hawk_credentials_setting,
        endpoint,
    ):
        page_length = wrapped_union_queryset.count()
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            with mock.patch(
                "django.conf.settings.HAWK_CREDENTIALS", hawk_credentials_setting
            ):
                response = logged_in_client.get(
                    endpoint, HTTP_AUTHORIZATION=hawk_authentication_header
                )
                json = response.json()
                next_page_link = json["next"]
                url_parts = urlparse(next_page_link)
                next_page_path = url_parts.path
                if url_parts.query:
                    next_page_path = f"{next_page_path}?{url_parts.query}"
                hawk_authentication_header = get_hawk_header(
                    access_key_id=hawk_credentials_setting["testsettings"]["id"],
                    secret_access_key=hawk_credentials_setting["testsettings"]["key"],
                    method="GET",
                    host="testserver",
                    port="80",
                    path=next_page_path,
                    content_type=b"",
                    content=b"",
                )
                response = logged_in_client.get(
                    next_page_link, HTTP_AUTHORIZATION=hawk_authentication_header
                )
                json = response.json()
                assert len(json["orderedItems"]) == 0

    def test_multiple_pages_have_items_in_order_of_last_modified_date_ascending(
        self,
        wrapped_union_queryset,
        logged_in_client,
        hawk_credentials_setting,
        endpoint,
    ):
        page_length = (
            wrapped_union_queryset.count() // 3
        )  # ensure things are spread over several pages
        with mock.patch(
            "activity_stream.pagination.ActivityStreamCursorPagination.get_page_size",
            return_value=int(page_length),
        ):
            results = []
            with mock.patch(
                "django.conf.settings.HAWK_CREDENTIALS", hawk_credentials_setting
            ):
                while endpoint:
                    url_parts = urlparse(endpoint)
                    next_page_path = url_parts.path
                    if url_parts.query:
                        next_page_path = f"{next_page_path}?{url_parts.query}"
                    hawk_authentication_header = get_hawk_header(
                        access_key_id=hawk_credentials_setting["testsettings"]["id"],
                        secret_access_key=hawk_credentials_setting["testsettings"][
                            "key"
                        ],
                        method="GET",
                        host="testserver",
                        port="80",
                        path=next_page_path,
                        content_type=b"",
                        content=b"",
                    )
                    response = logged_in_client.get(
                        endpoint, HTTP_AUTHORIZATION=hawk_authentication_header
                    )
                    json = response.json()
                    items = json["orderedItems"]
                    results += [
                        earlier["object"]["last_modified"]
                        <= later["object"]["last_modified"]
                        for earlier, later in zip(items[:-1], items[1:])
                    ]
                    endpoint = json.get("next", None)
            assert all(results)
