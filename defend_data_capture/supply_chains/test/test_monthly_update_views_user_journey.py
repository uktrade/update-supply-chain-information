import pytest

from django.test import Client
from django.urls import reverse

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


def prepare_stuff(
    url_name, with_monthly_update=True, with_monthly_update_url_kwarg=True
):
    strategic_action: StrategicAction = StrategicActionFactory()
    url_kwargs = {
        "strategic_action_id": strategic_action.pk,
    }
    if with_monthly_update:
        monthly_update: StrategicActionUpdate = strategic_action.monthly_updates.create(
            status=StrategicActionUpdate.Status.IN_PROGRESS,
            supply_chain=strategic_action.supply_chain,
        )
        if with_monthly_update_url_kwarg:
            url_kwargs["id"] = monthly_update.pk
    else:
        monthly_update = None
    url = reverse(url_name, kwargs=url_kwargs)
    return strategic_action, monthly_update, url


@pytest.mark.django_db()
class TestMonthlyUpdateCreationView:
    def test_create_monthly_update_redirects_if_current_monthly_update_exists(self):
        strategic_action, monthly_update, create_monthly_update_url = prepare_stuff(
            "monthly-update-create", with_monthly_update_url_kwarg=False
        )
        expected_redirect_url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.get(create_monthly_update_url, follow=False)
        assert response.status_code == 302
        assert response.url == expected_redirect_url

    def test_create_monthly_update_creates_new_monthly_update_and_redirects_to_it(self):
        strategic_action, _, create_monthly_update_url = prepare_stuff(
            "monthly-update-create", with_monthly_update=False
        )
        assert strategic_action.monthly_updates.exists() is False
        client = Client()
        response = client.get(create_monthly_update_url, follow=False)
        assert response.status_code == 302
        strategic_action.refresh_from_db()
        assert strategic_action.monthly_updates.exists() is True
        monthly_update = strategic_action.monthly_updates.get()
        expected_redirect_url = reverse(
            "monthly-update-info-edit",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        assert response.status_code == 302
        assert response.url == expected_redirect_url


@pytest.mark.django_db()
class TestMonthlyUpdateWithoutCompletionDate:
    def test_monthly_update_info_page_redirects_to_timing_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-info-edit"
        )
        strategic_action.target_completion_date = None
        strategic_action.save()
        data = {"content": "This is the content we are sending."}
        expected_response_url = reverse(
            "monthly-update-timing-edit",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_monthly_update_timing_page_redirects_to_status_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-timing-edit"
        )
        strategic_action.target_completion_date = None
        strategic_action.save()
        data = {"is_completion_date_known": False}
        expected_response_url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_monthly_update_status_page_redirects_to_summary_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-status-edit"
        )
        strategic_action.target_completion_date = None
        strategic_action.save()
        data = {"implementation_rag_rating": "GREEN"}
        expected_response_url = reverse(
            "monthly-update-summary",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url


@pytest.mark.django_db()
class TestMonthlyUpdateWithCompletionDate:
    def test_info_page_redirects_to_status_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-info-edit"
        )
        data = {"content": "This is the content we are sending."}
        expected_response_url = reverse(
            "monthly-update-status-edit",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_green_status_redirects_to_summary_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-status-edit"
        )
        data = {"implementation_rag_rating": "GREEN"}
        expected_response_url = reverse(
            "monthly-update-summary",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_amber_status_redirects_to_summary_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-status-edit"
        )
        data = {"implementation_rag_rating": "AMBER"}
        expected_response_url = reverse(
            "monthly-update-summary",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_red_status_with_changed_completion_date_redirects_to_revised_timing_page(
        self,
    ):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-status-edit"
        )
        data = {
            "implementation_rag_rating": "RED",
            "RED-will_completion_date_change": True,
        }
        expected_response_url = reverse(
            "monthly-update-revised-timing-edit",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_red_status_with_unchanged_completion_date_redirects_to_summary_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-status-edit"
        )
        data = {
            "implementation_rag_rating": "RED",
            "RED-will_completion_date_change": False,
        }
        expected_response_url = reverse(
            "monthly-update-summary",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url

    def test_revised_timing_redirects_to_summary_page(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-revised-timing-edit"
        )
        data = {"is_completion_date_known": False}
        expected_response_url = reverse(
            "monthly-update-summary",
            kwargs={
                "strategic_action_id": strategic_action.pk,
                "id": monthly_update.pk,
            },
        )
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 302
        assert response.url == expected_response_url


@pytest.mark.django_db()
class TestMonthlyUpdateTimingPage:
    def test_monthly_update_timing_page_requires_completion_date_if_known(self):
        strategic_action, monthly_update, info_url = prepare_stuff(
            "monthly-update-timing-edit"
        )
        strategic_action.target_completion_date = None
        strategic_action.save()
        data = {"is_completion_date_known": True}
        client = Client()
        response = client.post(info_url, data=data)
        assert response.status_code == 200
        # assert response.url == info_url
