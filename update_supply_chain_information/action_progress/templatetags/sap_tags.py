from django.template.defaulttags import register
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import date as date_tag

from supply_chains.models import StrategicAction


@register.simple_tag
def get_sap_filter_route(dept) -> str:
    """Return URL for the filter to post the form"""
    if dept:
        route = reverse("action-progress-department", kwargs={"dept": dept})
    else:
        route = reverse("action-progress")

    return route


@register.simple_tag
def get_action_completion(action_slug: str, supply_chain: object) -> str:
    """Return either completion date or Ongoing in string format"""
    completion = ""

    if action_slug:
        sa = get_object_or_404(
            StrategicAction, slug=action_slug, supply_chain=supply_chain
        )

        if sa.is_ongoing:
            completion = "Ongoing"
        else:
            completion = (
                date_tag(sa.target_completion_date, "j M Y") or "No information"
            )

    return completion
