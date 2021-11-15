import pytest


from accounts.test.factories import GovDepartmentFactory
from action_progress.forms import SAPForm


pytestmark = pytest.mark.django_db


class TestSAPForm:
    def test_sap_empty_form(self):
        # Arrange
        # Act
        form = SAPForm()

        # Assert
        assert not form.is_valid()

    def test_sap_init_form(self):
        # Arrange
        dept = GovDepartmentFactory()
        d = {"department": str(dept.id)}

        # Act
        form = SAPForm(data=d)

        # Assert
        assert form.is_valid()
