from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.filter()
def currency(amount):
    value = u'{:.2f}'.format(float(amount))
    dollar = u'{:,}'.format(int(amount))
    cents = value.split('.')[1]
    return mark_safe(
        u'<span class="currency" data-value="{0}">'
        '<span class="label">$</span>'
        '<span class="dollar">{1}</span>'
        '<span class="cents">.{2}</span>'
        '</span>'.format(value, dollar, cents))
