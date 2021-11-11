from django.template.defaulttags import register


@register.simple_tag
def getattribute_value(obj: object, attribute: str) -> object:
    """Return value of the attribute from given object"""
    if hasattr(obj, attribute):
        return getattr(obj, attribute)
    else:
        raise Exception(f"{attribute} not found within {obj}")


@register.simple_tag
def get_ints(min, max):
    """Return range based iterator with given min and max"""
    return range(min, max)


@register.simple_tag
def get_vul_stage_title(iterable: object, index: str) -> str:
    """Return title based on the index"""
    return iterable[int(index)]
