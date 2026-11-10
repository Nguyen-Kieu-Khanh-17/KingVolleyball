from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='vnd')
def vnd(value):
    """
    Format a number or Decimal with dot thousand separators.
    Example: 83250 -> 83.250
             1008100 -> 1.008.100
    """
    if value is None or value == '':
        return '0'
    try:
        val = float(value)
        return '{:,.0f}'.format(val).replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter(name='currency')
def currency(value):
    return vnd(value)

