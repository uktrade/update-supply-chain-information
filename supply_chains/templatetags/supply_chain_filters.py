import os

from django.template.defaulttags import register


@register.filter
def env(key):
    return os.environ.get(key, "")
