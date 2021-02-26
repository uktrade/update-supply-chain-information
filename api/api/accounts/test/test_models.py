import pytest

from django.core.exceptions import ValidationError

from api.accounts.models import GovDepartment
from api.accounts.test.factories import GovDepartmentFactory


@pytest.mark.django_db()
def test_gov_department_email_domains_unique():
    """
    Test that a government department cannot be saved to the database
    if one of its email_domains already exists for another department.
    """
    GovDepartmentFactory(email_domains=["domain.gov.uk", "email.gov.uk"])
    new_dep = GovDepartment(name="New Dep", email_domains=["domain.gov.uk"])
    with pytest.raises(ValidationError):
        new_dep.save()
