from django import template

register = template.Library()

@register.filter
def min_value(value, arg):
    """Retorna el menor valor entre value y arg"""
    try:
        return min(float(value), float(arg))
    except (ValueError, TypeError):
        return value

@register.filter
def max_value(value, arg):
    """Retorna el mayor valor entre value y arg"""
    try:
        return max(float(value), float(arg))
    except (ValueError, TypeError):
        return value