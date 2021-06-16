from django.template.defaulttags import register

from accounts.models import User


@register.simple_tag
def get_feedback_emails_as_string() -> str:
    """Formats emails as comma separated string to be passed to a mailto link"""
    users = User.objects.filter(receive_feedback_emails=True)
    emails = [user.email for user in users]
    return ",".join(emails)
