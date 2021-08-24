from django import forms

from accounts.models import GovDepartment
from supply_chains.models import SupplyChain


class SAPForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=GovDepartment.objects.all(),
        empty_label="Select department",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
                "aria-label": "department",
                "onchange": "form.submit();",
            }
        ),
        required=True,
        error_messages={
            "required": "You must select a department to continue",
        },
    )

    supply_chain = forms.ModelChoiceField(
        queryset=SupplyChain.objects.none(),
        empty_label="Select supply chain",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
                "aria-label": "supply_chain",
            }
        ),
        required=False,
        error_messages={
            "required": "You must select a supply chain to continue",
        },
    )

    def __init__(self, *args, **kwargs) -> None:
        qs = kwargs.pop("supply_chain_qs", None)
        sc_filter_status = kwargs.pop("supply_chain_required", False)
        super().__init__(*args, **kwargs)

        self.fields["supply_chain"].required = sc_filter_status

        if qs:
            self.fields["supply_chain"].queryset = qs
