import pytest

from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestAdminLogin:
    def test_login_unauthenticated(self, monkeypatch):
        """Test unauthenticated user is redirected to auth login url."""
        monkeypatch.setenv("ALLOWED_HOSTS", "localhost, sso.trade.gov.uk")
        client = Client()
        response = client.get(reverse("admin:index"), follow=True)
        assert response.request["PATH_INFO"] == "/o/authorize/"

    def test_login_authenticated_not_staff(self, logged_in_client):
        """Test authenticated user is redirected to index if not staff."""
        response = logged_in_client.get(reverse("admin:index"), follow=True)
        assert response.status_code == 200
        assert response.request["PATH_INFO"] == reverse("index")

    def test_login_authenticated_and_staff(self, logged_in_client, test_user):
        """Test authenticated user successfully reaches admin index when staff."""
        test_user.is_staff = True
        test_user.save()
        response = logged_in_client.get(reverse("admin:index"), follow=True)
        assert response.status_code == 200
        assert response.request["PATH_INFO"] == reverse("admin:index")
