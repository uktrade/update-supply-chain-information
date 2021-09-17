from django import template

register = template.Library()


@register.inclusion_tag("gsc_notes.html")
def gsc_notes(instance):
    changed_by_text = updated_on_text = update_text = review_text = ""
    if instance.gsc_last_changed_by:
        changed_by_text = f" by {instance.gsc_last_changed_by}"
    if instance.gsc_updated_on:
        updated_on_text = f" on {instance.gsc_updated_on}"
    if changed_by_text or updated_on_text:
        update_text = f"Last updated{changed_by_text}{updated_on_text}"
    if instance.gsc_review_on:
        review_text = f"To be reviewed on {instance.gsc_review_on}"
    return {
        "update_text": update_text,
        "review_text": review_text,
    }
