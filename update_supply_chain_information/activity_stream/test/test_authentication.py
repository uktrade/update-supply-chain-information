from unittest import mock

import pytest
from django.conf import settings
from django.urls import reverse

from activity_stream.test.util.hawk import get_hawk_header

pytestmark = pytest.mark.django_db


class TestHawkAuthentication:
    def test_no_hawk_authorisation_header_returns_forbidden(
        self, hawk_authentication_header, endpoint, client
    ):
        response = client.get(endpoint)
        assert response.status_code == 401  # Forbidden

    def test_valid_hawk_authorisation_header_returns_ok(
        self,
        hawk_credentials_setting,
        hawk_authentication_header,
        endpoint,
        logged_in_client,
    ):
        with mock.patch(
            "django.conf.settings.HAWK_CREDENTIALS", hawk_credentials_setting
        ):
            response = logged_in_client.get(
                f"{endpoint}", HTTP_AUTHORIZATION=hawk_authentication_header
            )
            assert response.status_code == 200  # OK
