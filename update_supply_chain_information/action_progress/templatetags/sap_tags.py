from django.template.defaulttags import register
from django.urls import reverse


@register.simple_tag
def get_sap_filter_route(dept) -> str:
    """Return URL for the filter to post the form"""
    if dept:
        route = reverse("action-progress-department", kwargs={"dept": dept})
    else:
        route = reverse("action-progress")

    return route
