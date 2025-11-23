# core/templatetags/dict_extras.py
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Return dictionary[key] trying both string and original key forms.
    Usage in template: {{ mydict|get_item:some_key }}
    """
    if dictionary is None:
        return None
    try:
        return dictionary.get(str(key)) or dictionary.get(key)
    except Exception:
        return None
