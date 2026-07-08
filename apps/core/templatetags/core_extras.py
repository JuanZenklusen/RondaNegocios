from django import template

register = template.Library()


@register.filter
def dict_get(mapping, key):
    """Devuelve mapping[key] en templates (para dicts con clave variable)."""
    if hasattr(mapping, "get"):
        return mapping.get(key)
    return None
