import pytest

from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestAdminViews:
    def test_index_redirects_to_login_unauthenticated(self):
        """Test unauthenticated user is redirected to admin login."""
        client = Client()
        expected_redirect_url = reverse("admin:login") + "?next=/admin/"
        response = client.get(reverse("admin:index"))
        assert response.status_code == 302
        assert response.url == expected_redirect_url

    def test_index_redirects_to_login_authenticated(self, logged_in_client):
        """Test authenticated user is redirected to admin login."""
        expected_redirect_url = reverse("admin:login") + "?next=/admin/"
        response = logged_in_client.get(reverse("admin:index"))
        assert response.status_code == 302
        assert response.url == expected_redirect_url

    def test_login_unauthenticated(self):
        """Test unauthenticated user is redirected to index."""
        client = Client()
        response = client.get(reverse("admin:login"))
        assert response.status_code == 302
        assert response.url == reverse("index")

    def test_login_authenticated_not_staff(self, logged_in_client):
        """Test authenticated user is redirected to index if not staff."""
        response = logged_in_client.get(reverse("admin:login"))
        assert response.status_code == 302
        assert response.url == reverse("index")

    def test_login_authenticated_and_staff(self, logged_in_client, test_user):
        """Test authenticated user successfully reaches admin index when staff."""
        test_user.is_staff = True
        test_user.save()
        response = logged_in_client.get(reverse("admin:login"))
        assert response.status_code == 302
        assert response.url == reverse("admin:index")
