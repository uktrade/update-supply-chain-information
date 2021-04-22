from datetime import date

from dateutil.relativedelta import relativedelta
from django import forms
from django.db.models import TextChoices
from django.forms.utils import ErrorList

from .widgets import (
    DetailSelectMixin,
    DetailRadioSelect,
    HintedDetailRadioSelect,
    DateMultiTextInputWidget,
)
from .models import StrategicActionUpdate, RAGRatingHints, StrategicAction


class DetailFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._detail_forms_dict = {}
        for field_name, key, config in self.detail_forms:
            try:
                form_class = config["form_class"]
                kwargs["prefix"] = key
                config["form"] = form_class(*args, **kwargs)
                self._detail_forms_dict[key] = config["form"]
            except KeyError:
                pass

    def detail_form_for_key(self, key):
        return self._detail_forms_dict[key]

    def is_valid(self):
        # this should only be called for the option that's selected
        valid = super().is_valid()
        for field_name, key, config in self.detail_forms:
            if self.cleaned_data[field_name] == key:
                valid = config["form"].is_valid() and valid
        return valid

    def save(self, commit=True):
        for field_name, key, config in self.detail_forms:
            # no need to commit if the instances are the same
            # as the outer form will do that below (if commit=True)
            # N.B. this assumes inner forms are using the same instance
            # But sometimes maybe they aren't… best check for it
            # If they aren't, we need to commit iff commit=True
            inner_commit = (self.instance != config["form"].instance) and commit
            if self.cleaned_data[field_name] == key:
                config["form"].save(commit=inner_commit)
        return super().save(commit=commit)

    @property
    def detail_forms(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, DetailSelectMixin):
                for key, config in field.widget.details.items():
                    yield (field_name, key, config)


class YesNoChoices(TextChoices):
    YES = (True, "Yes")
    NO = (False, "No")


class MonthlyUpdateInfoForm(forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = [
            "content",
        ]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "govuk-textarea",
                }
            )
        }


class AmberReasonForDelayForm(forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ["reason_for_delays"]
        labels = {"reason_for_delays": "Explain potential risk"}
        widgets = {
            "reason_for_delays": forms.Textarea(attrs={"class": "govuk-textarea"})
        }


class RedReasonForDelayForm(AmberReasonForDelayForm):

    will_completion_date_change = forms.ChoiceField(
        choices=YesNoChoices.choices,
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="Will the estimated completion date change?",
    )

    class Meta(AmberReasonForDelayForm.Meta):
        labels = {"reason_for_delays": "Explain issue"}


class MonthlyUpdateStatusForm(DetailFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        strategic_action_update: StrategicActionUpdate = kwargs.get("instance", None)
        if strategic_action_update is not None:
            if strategic_action_update.strategic_action.target_completion_date is None:
                will_completion_date_change_field = self.detail_form_for_key(
                    "RED"
                ).fields["will_completion_date_change"]
                will_completion_date_change_field.required = False

    class Meta:
        model = StrategicActionUpdate
        fields = ["implementation_rag_rating"]
        widgets = {
            "implementation_rag_rating": HintedDetailRadioSelect(
                attrs={
                    "class": "govuk-radios__input",
                    "data-aria-controls": "{id}-detail",
                },
                hints=RAGRatingHints,
                details={
                    "RED": {
                        "template": "supply_chains/includes/reason-for-delays.html",
                        "form_class": RedReasonForDelayForm,
                    },
                    "AMBER": {
                        "template": "supply_chains/includes/reason-for-delays.html",
                        "form_class": AmberReasonForDelayForm,
                    },
                },
            )
        }
        labels = {"implementation_rag_rating": "Current delivery status"}


class MakeFieldRequiredMixin:
    field_to_make_required = None

    def make_field_required(self):
        if self.field_to_make_required is not None:
            self.fields[self.field_to_make_required].required = True

    def make_field_not_required(self):
        if self.field_to_make_required is not None:
            self.fields[self.field_to_make_required].required = False


class CompletionDateForm(MakeFieldRequiredMixin, forms.ModelForm):
    target_completion_date = forms.DateField(
        widget=DateMultiTextInputWidget(
            attrs={},
            hint="For example 14 11 2021",
            labels={
                "day": "Day",
                "month": "Month",
                "year": "Year",
            },
        ),
        label="Date for intended completion",
        required=False,
        input_formats=["%Y-%m-%d"],
    )
    field_to_make_required = "target_completion_date"

    class Meta:
        model = StrategicAction
        fields = ["target_completion_date"]


class ApproximateTimings(TextChoices):
    THREE_MONTHS = ("3", "3 months")
    SIX_MONTHS = ("6", "6 months")
    ONE_YEAR = ("12", "1 year")
    TWO_YEARS = ("24", "2 years")
    ONGOING = ("0", "Ongoing")


class ApproximateTimingForm(MakeFieldRequiredMixin, forms.ModelForm):
    surrogate_is_ongoing = forms.ChoiceField(
        choices=ApproximateTimings.choices,
        label="What is the approximate time for completion?",
        required=False,
    )
    field_to_make_required = "surrogate_is_ongoing"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["surrogate_is_ongoing"].widget = forms.RadioSelect(
            choices=self.fields["surrogate_is_ongoing"].choices,
            attrs={
                "class": "govuk-radios__input",
            },
        )

    def save(self, commit=True):
        submitted_value = self.cleaned_data["surrogate_is_ongoing"]
        # As this form's field doesn't really exist
        if submitted_value == ApproximateTimings["ONGOING"]:
            # we need to either clear the completion date and set is_ongoing…
            self.instance.target_completion_date = None
            self.instance.is_ongoing = True
        else:
            # or calculate the new completion date and clear is_ongoing
            self.instance.is_ongoing = False
            months_hence = int(submitted_value)
            self.instance.target_completion_date = date.today() + relativedelta(
                months=+months_hence
            )

        return super().save(commit)

    class Meta:
        model = StrategicAction
        fields = []
        labels = {
            "surrogate_is_ongoing": "What is the approximate time for completion?",
        }


class MonthlyUpdateTimingForm(DetailFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if self.is_bound:
            # need to make one of the detail forms required, depending on our value
            is_completion_date_known = self.data["is_completion_date_known"]
            required_form = self.detail_form_for_key(is_completion_date_known)
            if required_form is not None:
                # we need the detail form required for validation,
                # but not on the client as then they can't change their minds…
                required_form.make_field_required()
                is_valid = super().is_valid()
                required_form.make_field_not_required()
                return is_valid
        return self.is_valid()

    is_completion_date_known = forms.ChoiceField(
        required=True,
        choices=YesNoChoices.choices,
        widget=DetailRadioSelect(
            attrs={"class": "govuk-radios__input", "data-aria-controls": "{id}-detail"},
            details={
                "True": {
                    "template": "supply_chains/includes/completion-date.html",
                    "form_class": CompletionDateForm,
                },
                "False": {
                    "template": "supply_chains/includes/approximate-timing.html",
                    "form_class": ApproximateTimingForm,
                },
            },
            select_label="Is there an expected completion date?",
        ),
    )

    class Meta:
        model = StrategicAction
        fields = []
        labels = {"is_completion_date_known": "Is there an expected completion date?"}
