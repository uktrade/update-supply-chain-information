import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from api.accounts.test.factories import UserFactory
from api.accounts.models import User


@pytest.mark.django_db()
def test_fails_if_unauthenticated():
    """
    Test that a 401 is returned if a request is made to the
    '/users' endpoint from an unauthenticated user.
    """
    url = reverse("user-list")
    client = APIClient()
    response = client.get(
        url,
    )
    assert response.status_code == 401


@pytest.mark.django_db()
def test_get_all_users(test_user, test_client_with_token):
    """
    Test that all users are returned when an authorised
    request is made to the '/users' endpoint.
    """
    num_users = User.objects.count()
    client = test_client_with_token
    url = reverse("user-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == num_users
    assert response.data[0]["id"] == str(test_user.id)


@pytest.mark.django_db()
def test_get_user_by_id(test_client_with_token):
    """
    Test that the relevant user object is returned when
    passing an id to the '/users' endpoint.
    """
    u = UserFactory()
    client = test_client_with_token
    url = reverse("user-detail", kwargs={"pk": u.id})
    response = client.get(url)
    assert response.status_code == 200
    assert response.data["id"] == str(u.id)
