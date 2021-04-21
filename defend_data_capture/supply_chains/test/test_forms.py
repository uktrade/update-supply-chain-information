from datetime import date

import pytest

from supply_chains.forms import (
    CompletionDateForm,
    MonthlyUpdateInfoForm,
    MonthlyUpdateStatusForm,
    MonthlyUpdateTimingForm,
)
from supply_chains.models import StrategicAction, StrategicActionUpdate
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
class TestCompletionDateForm:
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
class TestDeliveryStatusForm:
    def test_form_saves_the_status_when_GREEN(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": "GREEN"}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_status_when_AMBER(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": "AMBER"}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_reason_for_delays_when_AMBER(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": "AMBER",
            "AMBER-reason_for_delays": "A reason",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert saved_instance.reason_for_delays == form_data["AMBER-reason_for_delays"]

    def test_form_saves_the_status_when_RED_and_no_completion_date(self):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(
            supply_chain=supply_chain, target_completion_date=None
        )
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": "RED"}
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
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {"implementation_rag_rating": "RED"}
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert not form.is_valid()

    def test_form_saves_the_status_when_RED_with_completion_date_and_completion_date_change_is_true(
        self,
    ):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": "RED",
            "RED-will_completion_date_change": "True",
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
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": "RED",
            "RED-will_completion_date_change": "False",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        print(form.errors)
        for field_name, key, config in form.detail_forms:
            print(config["form"].errors)
        assert form.is_valid()
        saved_instance = form.save()
        assert (
            saved_instance.implementation_rag_rating
            == form_data["implementation_rag_rating"]
        )

    def test_form_saves_the_reason_for_delays_when_RED_with_completion_date_and_completion_date_change_is_true(
        self,
    ):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": "RED",
            "RED-will_completion_date_change": "True",
            "RED-reason_for_delays": "Some reason",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert saved_instance.reason_for_delays == form_data["RED-reason_for_delays"]

    def test_form_saves_the_reason_for_delays_when_RED_with_completion_date_and_completion_date_change_is_false(
        self,
    ):
        supply_chain = SupplyChainFactory()
        strategic_action = StrategicActionFactory(supply_chain=supply_chain)
        strategic_action_update = StrategicActionUpdate.objects.create(
            supply_chain=supply_chain, strategic_action=strategic_action
        )
        assert strategic_action_update.implementation_rag_rating is None

        form_data = {
            "implementation_rag_rating": "RED",
            "RED-will_completion_date_change": "False",
            "RED-reason_for_delays": "Some reason",
        }
        form = MonthlyUpdateStatusForm(data=form_data, instance=strategic_action_update)
        assert form.is_valid()
        saved_instance = form.save()
        assert saved_instance.reason_for_delays == form_data["RED-reason_for_delays"]
