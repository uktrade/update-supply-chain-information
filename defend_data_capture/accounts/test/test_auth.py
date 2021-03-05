import pytest

from accounts.models import GovDepartment
from accounts.test.factories import GovDepartmentFactory
from accounts.auth import (
    CustomAuthbrokerBackend,
    get_gov_department_id_from_user_email,
)


@pytest.mark.django_db()
def test_get_gov_department_id_from_user_email():
    """
    Test that the correct department id is returned according to
    the email passed in.
    """
    gov_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    email = "mr.test@email.gov.uk"
    gov_department_id = get_gov_department_id_from_user_email(email)
    assert gov_department_id == gov_department.id


@pytest.mark.django_db()
def test_user_mapping_adds_gov_department_id():
    """
    Test that when create_user_mapping is called, an object with
    a gov_department_id is returned with the correct id attached.
    """
    gov_department = GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "email": "mr.test@email.gov.uk",
        "first_name": "Mr",
        "last_name": "Test",
    }
    auth_backend = CustomAuthbrokerBackend()
    new_profile = auth_backend.user_create_mapping(mock_profile)
    assert new_profile["gov_department_id"] == gov_department.id


@pytest.mark.django_db()
def test_unauthenticated_user():
    """
    Test that when a user with an unlisted email domain attempts to login,
    government_department_id is None is returned.
    """
    GovDepartmentFactory(email_domains=["email.gov.uk"])
    mock_profile = {
        "email": "mr.unauth@shouldfail.gov.uk",
        "first_name": "Mr",
        "last_name": "Unauth",
    }
    auth_backend = CustomAuthbrokerBackend()
    new_profile = auth_backend.user_create_mapping(mock_profile)
    assert new_profile["gov_department_id"] == None
