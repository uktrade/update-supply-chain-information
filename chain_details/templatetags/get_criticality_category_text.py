from django.template.defaulttags import register


@register.simple_tag
def get_criticality_category_text(details, criticality_type, detail_category):
    return details[criticality_type][detail_category]
