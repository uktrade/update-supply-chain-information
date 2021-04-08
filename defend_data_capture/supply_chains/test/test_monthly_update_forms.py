import pytest

from supply_chains.models import (
    StrategicAction,
    StrategicActionUpdate,
    SupplyChain,
)
from supply_chains.test.factories import (
    StrategicActionFactory,
    StrategicActionUpdateFactory,
    SupplyChainFactory,
)
from accounts.test.factories import GovDepartmentFactory

from supply_chains.forms import MonthlyUpdateInfoForm

# @pytest.mark.django_db()
# def test_monthly_update_info_form_creation_fails_without_strategic_action():
#     form_class = MonthlyUpdateInfoForm
