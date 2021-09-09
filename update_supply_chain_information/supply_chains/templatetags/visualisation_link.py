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
    return {"visualisation_url": visualisation_url}
