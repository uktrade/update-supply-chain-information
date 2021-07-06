from datetime import datetime
from typing import Dict


import pytest
from django import forms

from supply_chains.forms import (
    PartialRelationForm,
    SACompletionDateForm,
    StrategicActionEditForm,
)
from supply_chains.models import StrategicAction
from supply_chains.test.factories import StrategicActionFactory


pytestmark = pytest.mark.django_db


class TestSACompletionDateForm:
    def extract_form_data(self, date_str) -> Dict:
        date_tokens = date_str.split("-")
        return {
            "target_completion_date_year": date_tokens[0],
            "target_completion_date_month": date_tokens[1],
            "target_completion_date_day": date_tokens[2],
        }

    @pytest.mark.parametrize(
        "date_str, validity",
        (
            (
                "2021-07-01",
                True,
            ),
            (
                "2021-12-31",
                True,
            ),
            (
                "2002-1-1",
                True,
            ),
            (
                "02-01-01",
                False,
            ),
            (
                "02-01-2021",
                False,
            ),
            (
                "02-JAN-2021",
                False,
            ),
        ),
    )
    def test_form_validity(self, date_str, validity):
        # Arrange
        form_data = self.extract_form_data(date_str)

        # Act
        form = SACompletionDateForm(data=form_data)

        # Assert
        assert form.is_valid() == validity

    def test_form_data(self):
        # Arrange
        target_date = "2021-07-01"
        target_object = datetime.strptime(target_date, "%Y-%m-%d")
        form_data = self.extract_form_data(target_date)
        sa = StrategicActionFactory()

        # Act
        form = SACompletionDateForm(instance=sa, data=form_data)
        form.save()

        # Assert
        assert sa.target_completion_date == target_object.date()
        assert not sa.is_ongoing


class TestPartialRelationForm:
    def test_form(self):
        # Arrange
        sa = StrategicActionFactory()
        text_data = "abcdefg"
        field = "specific_related_products"
        form_data = {field: text_data}

        # Act
        form = PartialRelationForm(instance=sa, data=form_data)
        form.save()

        # Assert
        assert isinstance(form.fields[field], forms.CharField)
        assert sa.specific_related_products == text_data
        assert form.is_valid()


class TestTextAreaStrategicActionEditForm:
    def test_form(self):
        # Arrange
        description_data = "Sourcing oxygen"
        impact_data = "Major"
        other_dep_data = "Few entities"
        sa = StrategicActionFactory(
            category=StrategicAction.Category.DIVERSIFY,
            geographic_scope=StrategicAction.GeographicScope.ENGLAND_ONLY,
        )

        form_data = {
            "description": description_data,
            "impact": impact_data,
            "other_dependencies": other_dep_data,
        }

        # Act
        form = StrategicActionEditForm(instance=sa, data=form_data)
        # TODO: Enable save
        # form.save()

        # Assert
        assert all(
            [
                isinstance(form.fields[x], forms.CharField)
                for x in ["description", "impact", "other_dependencies"]
            ]
        )
