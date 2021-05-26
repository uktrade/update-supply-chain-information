from unittest import mock

import pytest

from accounts.test.factories import GovDepartmentFactory
from accounts.auth import (
    CustomAuthbrokerBackend,
)


@pytest.mark.django_db()
def test_backend_create_user_does_not_create_user_for_unknown_department():
    """
    Test that no user is created if the email domain is not from a known department.
    """
    gov_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "email": "mr.test@dosac.gov.uk",
        "email_user_id": "mr.test-1234@dosac.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
    }
    auth_backend = CustomAuthbrokerBackend()
    new_profile = auth_backend.create_user(mock_profile)
    assert new_profile is None


@pytest.mark.django_db()
def test_new_user_calls_user_manager_create_user_method():
    """
    Test that when create_user is called, object creation is achieved
    by calling the create_user method of models.UserManager.
    """
    gov_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "email": "mr.test@email.gov.uk",
        "email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
    }
    auth_backend = CustomAuthbrokerBackend()
    with mock.patch("accounts.models.UserManager.create_user") as mocked_method:
        new_profile = auth_backend.create_user(mock_profile)
        assert mocked_method.called


@pytest.mark.django_db()
def test_backend_create_user_creates_user_with_valid_data():
    """
    Test that the newly-created user has all the bits we intended them to have.
    """
    gov_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "email": "mr.test@email.gov.uk",
        "email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
    }
    auth_backend = CustomAuthbrokerBackend()
    new_profile = auth_backend.create_user(mock_profile)
    assert new_profile is not None
    assert new_profile.email == mock_profile["email"]
    assert new_profile.sso_email_user_id == mock_profile["email_user_id"]
    assert new_profile.first_name == mock_profile["first_name"]
    assert new_profile.last_name == mock_profile["last_name"]
