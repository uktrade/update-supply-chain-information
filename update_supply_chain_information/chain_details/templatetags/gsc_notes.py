from django import template
from django.template.defaultfilters import date as date_filter

register = template.Library()

date_format = "l d M Y"


@register.inclusion_tag("gsc_notes.html")
def gsc_notes(instance):
    changed_by_text = updated_on_text = update_text = review_text = ""

    if instance:
        if instance.gsc_last_changed_by:
            changed_by_text = f" by {instance.gsc_last_changed_by}"
        if instance.gsc_updated_on:
            updated_on_text = f" on {date_filter(instance.gsc_updated_on, date_format)}"
        if changed_by_text or updated_on_text:
            update_text = f"Last updated{changed_by_text}{updated_on_text}"
        if instance.gsc_review_on:
            review_text = (
                f"To be reviewed on {date_filter(instance.gsc_review_on, date_format)}"
            )
    return {
        "update_text": update_text,
        "review_text": review_text,
    }
