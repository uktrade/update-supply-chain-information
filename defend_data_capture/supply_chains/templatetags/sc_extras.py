from django import template

register = template.Library()


@register.filter
def boolean_status(value: str, truthy_value: str) -> str:
    if value.lower() == truthy_value.lower():
        return "Yes"
    else:
        return "No"
