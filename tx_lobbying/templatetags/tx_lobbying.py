from django import template
from django.utils.safestring import mark_safe
register = template.Library()


@register.filter()
def currency(amount):
    if amount is None or amount is '':
        return mark_safe(u'<span class="currency" data-value=""></span>')
    value = u'{:.2f}'.format(float(amount))
    dollar = u'{:,}'.format(int(amount))
    cents = value.split('.')[1]
    additional_class = ''
    if dollar == '0' and cents == '00':  # avoid checking type of amount
        additional_class = ' zero'
    # WISHLIST handle negative
    return mark_safe(
        u'<span class="currency{3}" data-value="{0}">'
        '<span class="label">$</span>'
        '<span class="dollar">{1}</span>'
        '<span class="cents">.{2}</span>'
        '</span>'.format(value, dollar, cents, additional_class))
