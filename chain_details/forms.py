from django import forms

from accounts.models import GovDepartment


class SCDForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=GovDepartment.objects.all(),
        empty_label="Select department",
        widget=forms.Select(
            attrs={
                "class": "govuk-select",
                "aria-label": "department",
            }
        ),
        required=True,
        error_messages={
            "required": "You must select a department to continue",
        },
    )
