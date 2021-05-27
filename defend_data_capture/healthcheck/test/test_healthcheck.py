import pytest

from django.test import Client
from django.urls import reverse

from healthcheck.constants import HealthStatus
from healthcheck.models import HealthCheck


@pytest.fixture
def expected_HTTP_headers():
    yield {
        "Content-Type": "text/xml",
        "Cache-Control": "no-cache, no-store, must-revalidate",
    }


class TestHealthCheckView:
    def test_503_response(self, expected_HTTP_headers):
        # Test has no access to db so should fail db_check()
        client = Client()
        response = client.get(reverse("healthcheck"))
        assert response.status_code == 503
        assert response.context["status"] == HealthStatus.FAIL
        assert response.context["response_time"] > 0
        assert response.headers["Content-Type"] == expected_HTTP_headers["Content-Type"]
        assert (
            response.headers["Cache-Control"] == expected_HTTP_headers["Cache-Control"]
        )

    @pytest.mark.django_db()
    def test_200_response(self, expected_HTTP_headers):
        client = Client()
        h = HealthCheck(health_check_field=True)
        h.save()
        response = client.get(reverse("healthcheck"))
        assert response.status_code == 200
        assert response.context["status"] == HealthStatus.OK
        assert response.context["response_time"] > 0
        assert response.headers["Content-Type"] == expected_HTTP_headers["Content-Type"]
        assert (
            response.headers["Cache-Control"] == expected_HTTP_headers["Cache-Control"]
        )
