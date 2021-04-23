import unittest
from datetime import date
from unittest import mock

from dateutil.relativedelta import relativedelta
import pytest

from supply_chains.forms import (
    CompletionDateForm,
    MonthlyUpdateInfoForm,
    MonthlyUpdateStatusForm,
    MonthlyUpdateTimingForm,
    YesNoChoices,
    ApproximateTimingForm,
    ApproximateTimings,
)
from supply_chains.models import StrategicAction, StrategicActionUpdate, RAGRating
from supply_chains.test.factories import StrategicActionFactory, SupplyChainFactory


@pytest.mark.django_db()
class TestCompletionDateForm:
    def test_form_acccepts_YYYY_M_D_date(self):
        date_string = "2021-1-1"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        form = CompletionDateForm(data=form_data)
        assert form.is_valid()

    def test_form_acccepts_YYYY_0M_0D_date(self):
        date_string = "2021-01-01"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        form = CompletionDateForm(data=form_data)
        assert form.is_valid()

    def test_form_acccepts_YYYY_M_0D_date(self):
        date_string = "2021-1-01"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        form = CompletionDateForm(data=form_data)
        assert form.is_valid()

    def test_form_acccepts_YYYY_0M_D_date(self):
        date_string = "2021-01-1"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        form = CompletionDateForm(data=form_data)
        assert form.is_valid()

    def test_form_accepts_YYYY_MM_DD_date(self):
        date_string = "2021-12-31"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        form = CompletionDateForm(data=form_data)
        assert form.is_valid()

    def test_form_rejects_malformed_date(self):
        date_string = "202-x-y"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        form = CompletionDateForm(data={"target_completion_date": form_data})
        assert not form.is_valid()

    def test_form_saves_the_date(self):
        date_string = "2021-12-31"
        date_parts = date_string.split("-")
        form_data = {
            "target_completion_date_year": date_parts[0],
            "target_completion_date_month": date_parts[1],
            "target_completion_date_day": date_parts[2],
        }
        strategic_action: StrategicAction = StrategicAction(
            start_date=date(year=2020, month=6, day=21),
            is_archived=False,
            supply_chain=SupplyChainFactory(),
        )
        assert strategic_action.target_completion_date is None
        form = CompletionDateForm(data=form_data, instance=strategic_action)
        assert form.is_valid()
        saved_instance = form.save()
        assert saved_instance.pk is not None
        assert strategic_action.target_completion_date is not None
        expected_date = date.fromisoformat(date_string)
        assert expected_date == saved_instance.target_completion_date


@pytest.mark.django_db()
class TestMonthlyUpdateInfoForm:
    def test_form_saves_the_content(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.content == ""

        form_data = {"content": "Now is the winter of our discontent"}
        form = MonthlyUpdateInfoForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert saved_instance.content == form_data["content"]


@pytest.mark.django_db()
class TestMonthlyUpdateStatusForm:
    def setup_method(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        self.strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )

    def test_form_saves_the_status_when_GREEN(self):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": RAGRating.GREEN}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_status_when_AMBER(self):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": RAGRating.AMBER}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_reason_for_delays_when_AMBER(self):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": RAGRating.AMBER,
            f"{RAGRating.AMBER}-reason_for_delays": "A reason",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert saved_instance.reason_for_delays == form_data["AMBER-reason_for_delays"]

    def test_form_saves_the_status_when_RED_and_no_completion_date(self):
        strategic_action_update = self.strategic_action_update
        strategic_action_update.strategic_action.target_completion_date = None
        strategic_action_update.strategic_action.save()
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": RAGRating.RED}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_invalid_when_RED_with_completion_date_and_no_will_completion_date_change(
        self,
    ):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": RAGRating.RED}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert not form.is_valid()

    def test_form_saves_the_status_when_RED_with_completion_date_and_completion_date_change_is_true(
        self,
    ):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": RAGRating.RED,
            f"{RAGRating.RED}-will_completion_date_change": "True",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_status_when_RED_with_completion_date_and_completion_date_change_is_false(
        self,
    ):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": RAGRating.RED,
            f"{RAGRating.RED}-will_completion_date_change": "False",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_reason_for_delays_when_RED_with_completion_date_and_completion_date_change_is_true(
        self,
    ):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": RAGRating.RED,
            f"{RAGRating.RED}-will_completion_date_change": "True",
            f"{RAGRating.RED}-reason_for_delays": "Some reason",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.reason_for_delays
            == form_data[f"{RAGRating.RED}-reason_for_delays"]
        )

    def test_form_saves_the_reason_for_delays_when_RED_with_completion_date_and_completion_date_change_is_false(
        self,
    ):
        strategic_action_update = self.strategic_action_update
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": RAGRating.RED,
            f"{RAGRating.RED}-will_completion_date_change": "False",
            f"{RAGRating.RED}-reason_for_delays": "Some reason",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.reason_for_delays
            == form_data[f"{RAGRating.RED}-reason_for_delays"]
        )


@pytest.mark.django_db()
class TestAmberReasonForDelayForm:
    """Nothing to test unless the reason_for_delays field is required."""

    pass


@pytest.mark.django_db()
class TestRedReasonForDelayForm:
    """Nothing to test unless the reason_for_delays field is required."""

    pass


@pytest.mark.django_db()
class TestApproximateTimingForm:
    """Should calculate and save the date, or set is_ongoing"""

    def setup_method(self):
        supply_chain = SupplyChainFactory()
        self.strategic_action: StrategicAction = StrategicActionFactory(
            supply_chain=supply_chain
        )
        # self.strategic_action_update = StrategicActionUpdate.objects.create(
        #     supply_chain=supply_chain, strategic_action=strategic_action
        # )

    def test_selecting_is_ongoing_sets_is_ongoing_and_clears_date(self):
        form_data = {"surrogate_is_ongoing": int(ApproximateTimings["ONGOING"])}
        self.strategic_action.target_completion_date = date(year=2022, month=4, day=22)
        self.strategic_action.is_ongoing = False
        self.strategic_action.save()
        form = ApproximateTimingForm(data=form_data, instance=self.strategic_action)
        assert form.is_valid()
        saved_instance: StrategicAction = form.save()
        assert saved_instance.target_completion_date is None
        assert saved_instance.is_ongoing

    def test_selecting_six_months_sets_correct_date_and_clears_is_ongoing(self):
        form_data = {"surrogate_is_ongoing": int(ApproximateTimings["SIX_MONTHS"])}
        self.strategic_action.target_completion_date = None
        self.strategic_action.is_ongoing = True
        self.strategic_action.save()

        expected_target_completion_date = date.today() + relativedelta(months=+6)
        form = ApproximateTimingForm(data=form_data, instance=self.strategic_action)
        assert form.is_valid()
        saved_instance: StrategicAction = form.save()
        assert saved_instance.target_completion_date == expected_target_completion_date
        assert saved_instance.is_ongoing is False

    def test_selecting_two_years_sets_correct_date_and_clears_is_ongoing(self):
        form_data = {"surrogate_is_ongoing": int(ApproximateTimings["TWO_YEARS"])}
        self.strategic_action.target_completion_date = None
        self.strategic_action.is_ongoing = True
        self.strategic_action.save()

        expected_target_completion_date = date.today() + relativedelta(years=+2)
        form = ApproximateTimingForm(data=form_data, instance=self.strategic_action)
        form_valid = form.is_valid()
        assert form_valid
        saved_instance: StrategicAction = form.save()
        assert saved_instance.target_completion_date == expected_target_completion_date
        assert saved_instance.is_ongoing is False

    def test_selecting_one_year_on_february_29th_sets_correct_date(self):
        form_data = {"surrogate_is_ongoing": int(ApproximateTimings["TWO_YEARS"])}
        self.strategic_action.target_completion_date = None
        self.strategic_action.is_ongoing = True
        self.strategic_action.save()

        # mocking datetime.date.today gets complicated…
        # see https://williambert.online/2011/07/how-to-unit-testing-in-django-with-mocking-and-patching/

        # class MockDate(date):
        #     def __new__(cls, *args, **kwargs):
        #         return date.__new__(date, *args, **kwargs)

        leap_year_day = date(year=2020, month=2, day=29)
        with mock.patch(
            "supply_chains.forms.date",
            mock.Mock(today=mock.Mock(return_value=leap_year_day)),
        ):
            expected_target_completion_date = leap_year_day + relativedelta(years=+2)
            form = ApproximateTimingForm(data=form_data, instance=self.strategic_action)
            form_valid = form.is_valid()
            assert form_valid
            saved_instance: StrategicAction = form.save()
            assert (
                saved_instance.target_completion_date == expected_target_completion_date
            )
            assert saved_instance.is_ongoing is False


@pytest.mark.django_db()
class TestMonthlyUpdateTimingForm:
    """Should either save the date, or calculate the date, or set is_ongoing."""

    def setup_method(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        self.strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )

    def test_completion_date_known_makes_completion_date_field_required(self):
        """If completion date is known, save completion date."""
        choices = YesNoChoices.choices
        selected_choice = choices[0]  # "Yes" choice
        form_data = {"is_completion_date_known": selected_choice[0]}  # value of choice
        form = MonthlyUpdateTimingForm(
            data=form_data, instance=self.strategic_action_update
        )
        assert not form.is_valid()
        detail_form = form.detail_form_for_key(selected_choice[0])
        assert not isinstance(detail_form, ApproximateTimingForm)
        assert isinstance(detail_form, CompletionDateForm)
        assert not detail_form.is_valid()
        assert "target_completion_date" in detail_form.errors.keys()

    def test_completion_date_not_known_makes_completion_date_form_not_used(self):
        """If completion date is not known, completion date form isn't used."""
        choices = YesNoChoices.choices
        selected_choice = choices[1]  # "No" choice
        form_data = {"is_completion_date_known": selected_choice[0]}  # value of choice
        form = MonthlyUpdateTimingForm(
            data=form_data, instance=self.strategic_action_update
        )
        detail_form = form.detail_form_for_key(selected_choice[0])
        assert not isinstance(detail_form, CompletionDateForm)
        assert isinstance(detail_form, ApproximateTimingForm)
        assert "target_completion_date" not in detail_form.fields.keys()

    def test_completion_date_not_known_uses_approximate_timing_form(self):
        """If completion date is not known, approximate timing form is used."""
        choices = YesNoChoices.choices
        selected_choice = choices[1]  # "No" choice
        form_data = {"is_completion_date_known": selected_choice[0]}  # value of choice
        form = MonthlyUpdateTimingForm(
            data=form_data, instance=self.strategic_action_update
        )
        detail_form = form.detail_form_for_key(selected_choice[0])
        assert "surrogate_is_ongoing" in detail_form.fields.keys()

    def test_completion_date_not_known_makes_approximate_timing_required(self):
        """If completion date is not known, approximate timing form is required."""
        choices = YesNoChoices.choices
        selected_choice = choices[1]  # "No" choice
        form_data = {"is_completion_date_known": selected_choice[0]}  # value of choice
        form = MonthlyUpdateTimingForm(
            data=form_data, instance=self.strategic_action_update
        )
        assert not form.is_valid()
        detail_form = form.detail_form_for_key(selected_choice[0])
        assert not detail_form.is_valid()
        assert "surrogate_is_ongoing" in detail_form.errors.keys()
