from django.conf import settings
from django.template.defaulttags import register
from django.urls import reverse

from accounts.models import User


@register.simple_tag
def get_feedback_emails_as_string() -> str:
    """Formats emails as comma separated string to be passed to a mailto link"""
    users = User.objects.filter(receive_feedback_emails=True)
    emails = [user.email for user in users]
    return ",".join(emails)


@register.simple_tag
def get_action_progress_route(user) -> str:
    """Return SAP route based on the logged in user"""
    route = None
    if user.is_admin:
        route = reverse("action-progress")
    else:
        route = reverse(
            "action-progress-department", kwargs={"dept": user.gov_department.name}
        )

    return route


@register.simple_tag(takes_context=True)
def get_active_menu(context):
    menu = None
    resolver = context["request"].resolver_match
    view_name, route = resolver.view_name, resolver.route

    if route.startswith("supply-chains/"):
        menu = "updates"
    if route.startswith("action-progress/"):
        menu = "sap"
    if route.startswith("chain-details/"):
        menu = "scd"
    if route == "" and view_name == "index":
        menu = "home"

    return menu


@register.simple_tag(takes_context=False)
def quicksight_countries_dashboard_url():
    return settings.QUICKSIGHT_COUNTRIES_DASHBOARD_URL
