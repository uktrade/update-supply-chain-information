from urllib.parse import urlencode

from django import template

register = template.Library()

link_template = template.Template(
    '<a href="{{ visualisation_url }}" class="temp-visual-link">Visuals</a>'
)


@register.inclusion_tag(link_template, takes_context=True)
def visualisation_link(context):
    request = context["request"]
    user = request.user
    gov_department = user.gov_department
    visualisation_url = gov_department.visualisation_url
    absolute_back_url = request.build_absolute_uri(request.path)
    back_url_query_string = urlencode({"back": absolute_back_url})
    backlinked_visualisation_url = f"{visualisation_url}?{back_url_query_string}"
    return {"visualisation_url": backlinked_visualisation_url}
