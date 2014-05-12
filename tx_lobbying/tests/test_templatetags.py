from django.template import Context, Template
from django.test import TestCase


class TemplatetagsTest(TestCase):
    def test_currency_handles_none(self):
        t = Template('{% load currency from tx_lobbying %}'
            '{{ amount|currency }}')
        c = Context({'amount': None})
        output = t.render(c)
        self.assertHTMLEqual(output,
            '<span class="currency" data-value=""></span>')

    def test_currency_rounds_right(self):
        t = Template('{% load currency from tx_lobbying %}'
            '{{ 1000.955|currency }}')
        c = Context()
        output = t.render(c)
        self.assertHTMLEqual(output,
            '<span class="currency" data-value="1000.96">'
            '<span class="label">$</span>'
            '<span class="dollar">1,000</span>'
            '<span class="cents">.96</span></span>')

    def test_currency_handles_numeric_string(self):
        t = Template('{% load currency from tx_lobbying %}'
            '{{ "10"|currency }}')
        c = Context()
        output = t.render(c)
        self.assertHTMLEqual(output,
            '<span class="currency" data-value="10.00">'
            '<span class="label">$</span>'
            '<span class="dollar">10</span>'
            '<span class="cents">.00</span></span>')

    def test_currency_handles_zero(self):
        t = Template('{% load currency from tx_lobbying %}'
            '{{ 0|currency }}')
        c = Context()
        output = t.render(c)
        self.assertHTMLEqual(output,
            '<span class="currency zero" data-value="0.00">'
            '<span class="label">$</span>'
            '<span class="dollar">0</span>'
            '<span class="cents">.00</span></span>')
