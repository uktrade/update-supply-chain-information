import pytest
from unittest import mock

from django.contrib.auth import get_user_model

from accounts.test.factories import GovDepartmentFactory
from accounts.models import get_gov_department_id_from_user_email, GovDepartment

UserModel = get_user_model()


@pytest.mark.django_db()
def test_gov_department_domains_lower_case():
    """
    Test that email_domains are set as lowercase before entering the database.
    """
    new_dep = GovDepartmentFactory(email_domains=["Domain.gov.uk", "EMAIL.GOV.UK"])
    lower_domains = ["domain.gov.uk", "email.gov.uk"]
    assert new_dep.email_domains == lower_domains


@pytest.mark.django_db()
def test_manager_create_user_creates_user():
    """
    Test that UserModel.objects.create_user does that.
    """
    new_dep = GovDepartmentFactory(
        email_domains=[
            "email.gov.uk",
        ]
    )
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
        "gov_department": new_dep,
    }
    email = "mr.test@email.gov.uk"
    new_profile = UserModel.objects.create_user(email=email, **mock_profile)
    assert new_profile is not None
    assert new_profile.email == email
    assert new_profile.sso_email_user_id == mock_profile["sso_email_user_id"]
    assert new_profile.first_name == mock_profile["first_name"]
    assert new_profile.last_name == mock_profile["last_name"]


@pytest.mark.django_db()
def test_manager_create_user_calls_set_unusable_password():
    """
    Test that UserModel.objects.create_user correctly prevents password login.
    """
    new_dep = GovDepartmentFactory(
        email_domains=[
            "email.gov.uk",
        ]
    )
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
        "gov_department": new_dep,
    }
    email = "mr.test@email.gov.uk"
    with mock.patch.object(UserModel, "set_unusable_password") as mocked_method:
        new_profile = UserModel.objects.create_user(email=email, **mock_profile)
        assert mocked_method.called


@pytest.mark.django_db()
def test_manager_create_user_adds_department_using_email_address():
    """
    Test that UserModel.objects.create_user sets the department.
    """
    expected_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
    }
    email = "mr.test@email.gov.uk"
    new_profile = UserModel.objects.create_user(email=email, **mock_profile)
    assert new_profile.gov_department == expected_department


@pytest.mark.django_db()
def test_manager_create_user_for_unknown_email_domain_returns_none():
    """
    Test that UserModel.objects.create_user returns None for an unknown email domain.
    """
    expected_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@dosac.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
    }
    email = "mr.test@dosac.gov.uk"
    new_profile = UserModel.objects.create_user(email=email, **mock_profile)
    assert new_profile is None


@pytest.mark.django_db()
def test_get_gov_department_id_from_user_email():
    """
    Test that the correct department id is returned according to
    the email passed in.
    """
    gov_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    email = "mr.test@email.gov.uk"
    gov_department_id = get_gov_department_id_from_user_email(email).id
    assert gov_department_id == gov_department.id


@pytest.mark.django_db()
def test_manager_create_superuser_creates_superuser():
    """
    Test that UserModel.objects.create_superuser does that.
    """
    new_dep = GovDepartmentFactory(
        email_domains=[
            "email.gov.uk",
        ]
    )
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
        "gov_department": new_dep,
    }
    email = "mr.test@email.gov.uk"
    new_profile = UserModel.objects.create_superuser(email=email, **mock_profile)
    assert new_profile.is_staff
    assert new_profile.is_superuser


@pytest.mark.django_db()
def test_manager_create_user_does_not_create_staff_user():
    """
    Test that a normal user isn't created as a staff user.
    """
    new_dep = GovDepartmentFactory(
        email_domains=[
            "email.gov.uk",
        ]
    )
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
        "gov_department": new_dep,
    }
    email = "mr.test@email.gov.uk"
    new_profile = UserModel.objects.create_user(email=email, **mock_profile)
    assert not new_profile.is_staff


@pytest.mark.django_db()
def test_manager_create_user_does_not_create_superuser():
    """
    Test that a normal user isn't created as a superuser.
    """
    new_dep = GovDepartmentFactory(
        email_domains=[
            "email.gov.uk",
        ]
    )
    mock_profile = {
        "sso_email_user_id": "mr.test-1234@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
        "gov_department": new_dep,
    }
    email = "mr.test@email.gov.uk"
    new_profile = UserModel.objects.create_user(email=email, **mock_profile)
    assert not new_profile.is_superuser
