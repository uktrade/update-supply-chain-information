from datetime import date

import pytest

from django import forms
from django.core.exceptions import ValidationError
from django.db import models

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

from supply_chains import forms as our_forms


# class TestModel(models.Model):
#     inner_form_content = models.TextField(default='', blank=True)
#     outer_form_content = models.TextField(default='', blank=True)
#
from supply_chains.widgets import DetailRadioSelect


class InnerTestDetailForm(forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ["reason_for_delays"]


class OuterTestDetailForm(our_forms.DetailFormMixin, forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ["implementation_rag_rating"]
        widgets = {
            "implementation_rag_rating": DetailRadioSelect(
                attrs={
                    "class": "govuk-radios__input",
                    "data-aria-controls": "{id}-detail",
                },
                details={
                    "RED": {
                        "template": "supply_chains/includes/reason-for-delays.html",
                        "form_class": InnerTestDetailForm,
                    },
                },
            )
        }


class InnerTestDetailInvalidForm(InnerTestDetailForm):
    def clean_reason_for_delays(self):
        raise ValidationError("Forcing a validation error for testing")


class OuterTestDetailInvalidForm(our_forms.DetailFormMixin, forms.ModelForm):
    class Meta:
        model = StrategicActionUpdate
        fields = ["implementation_rag_rating"]
        widgets = {
            "implementation_rag_rating": DetailRadioSelect(
                attrs={
                    "class": "govuk-radios__input",
                    "data-aria-controls": "{id}-detail",
                },
                details={
                    "RED": {
                        "template": "supply_chains/includes/reason-for-delays.html",
                        "form_class": InnerTestDetailInvalidForm,
                    },
                },
            )
        }


@pytest.mark.django_db()
class TestDetailForms:
    def test_detail_form_exposes_inner_form(self):
        outer_form = OuterTestDetailForm()
        assert hasattr(outer_form, "detail_forms")
        detail_forms = list(outer_form.detail_forms)
        assert len(detail_forms) == 1
        for key, config in outer_form.detail_forms:
            assert key == "RED"
            assert isinstance(config, dict)
            assert "form_class" in config.keys()
            assert isinstance(config["form_class"], InnerTestDetailForm.__class__)
            assert "form" in config
            assert isinstance(config["form"], InnerTestDetailForm)

    def test_detail_form_initialises_inner_form(self):
        outer_form = OuterTestDetailForm()
        assert hasattr(outer_form, "detail_forms")
        for _, config in outer_form.detail_forms:
            assert "form" in config
            assert isinstance(config["form"], InnerTestDetailForm)

    def test_detail_form_initialises_data_for_inner_form(self):
        expected_outer_form_field_value = "RED"
        expected_inner_form_field_value = "inner form field value"
        form_data = {
            "implementation_rag_rating": expected_outer_form_field_value,
            "RED-reason_for_delays": expected_inner_form_field_value,
        }
        outer_form = OuterTestDetailForm(data=form_data)
        for _, config in outer_form.detail_forms:
            inner_form = config["form"]
            assert inner_form.is_bound
            assert "reason_for_delays" in inner_form.fields.keys()
            actual_inner_form_field_value = inner_form.data["RED-reason_for_delays"]
            assert actual_inner_form_field_value == expected_inner_form_field_value

    def test_detail_form_validates_data_for_valid_inner_form(self):
        expected_outer_form_field_value = "RED"
        expected_inner_form_field_value = "inner form field value"
        form_data = {
            "implementation_rag_rating": expected_outer_form_field_value,
            "RED-reason_for_delays": expected_inner_form_field_value,
        }
        outer_form = OuterTestDetailForm(data=form_data)
        assert outer_form.is_valid()
        for _, config in outer_form.detail_forms:
            inner_form = config["form"]
            assert inner_form._errors is not None

    def test_detail_form_validates_data_for_invalid_inner_form(self):
        expected_outer_form_field_value = "RED"
        expected_inner_form_field_value = "inner form field value"
        form_data = {
            "implementation_rag_rating": expected_outer_form_field_value,
            "RED-reason_for_delays": expected_inner_form_field_value,
        }
        outer_form = OuterTestDetailInvalidForm(data=form_data)
        assert not outer_form.is_valid()
        for _, config in outer_form.detail_forms:
            inner_form = config["form"]
            assert inner_form._errors is not None
            assert "reason_for_delays" in inner_form.errors.keys()

    def test_detail_form_saves_data_for_inner_form(self):
        expected_outer_form_field_value = "RED"
        expected_inner_form_field_value = "inner form field value"
        strategic_action_update = StrategicActionUpdateFactory()
        form_data = {
            "implementation_rag_rating": expected_outer_form_field_value,
            "RED-reason_for_delays": expected_inner_form_field_value,
        }
        outer_form = OuterTestDetailForm(
            instance=strategic_action_update, data=form_data
        )
        outer_form.save()
        instance = outer_form.instance
        instance.refresh_from_db()
        assert instance.pk is not None
        assert instance.implementation_rag_rating == expected_outer_form_field_value
        assert instance.reason_for_delays == expected_inner_form_field_value
