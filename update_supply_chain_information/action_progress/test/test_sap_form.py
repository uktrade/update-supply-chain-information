import pytest


from accounts.test.factories import GovDepartmentFactory
from supply_chains.models import SupplyChain
from supply_chains.test.factories import SupplyChainFactory
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

    @pytest.mark.skip
    def test_sap_init_with_sc(self):
        # Arrange
        dept = GovDepartmentFactory()
        sc = SupplyChainFactory(gov_department=dept)

        d = {
            "department": str(dept.id),
            "supply_chain": str(sc.id),
        }

        # Act
        form = SAPForm(data=d)
        # print(form)
        print(f"SC: {sc.id}")
        print(f"DEPT: {dept.id}")
        print(SupplyChain.objects.values("id", "gov_department_id", "name", "slug"))
        print(d)
        print("\n\n")

        print(form.errors)
        # Assert
        assert form.is_valid()
