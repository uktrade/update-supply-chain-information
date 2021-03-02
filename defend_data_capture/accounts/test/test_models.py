import pytest

from accounts.test.factories import GovDepartmentFactory


@pytest.mark.django_db()
def test_gov_department_domains_lower_case():
    """
    Test that email_domains are set as lowercase before entering the database.
    """
    new_dep = GovDepartmentFactory(email_domains=["Domain.gov.uk", "EMAIL.GOV.UK"])
    lower_domains = ["domain.gov.uk", "email.gov.uk"]
    assert new_dep.email_domains == lower_domains
