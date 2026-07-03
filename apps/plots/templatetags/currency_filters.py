from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def currency(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    if value >= 1_000_000:
        formatted = value / 1_000_000
        return f'{formatted:.1f}M' if formatted != int(formatted) else f'{int(formatted)}M'
    elif value >= 1_000:
        formatted = value / 1_000
        return f'{formatted:.1f}K' if formatted != int(formatted) else f'{int(formatted)}K'
    return f'{value:,.0f}'
