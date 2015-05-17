from __future__ import unicode_literals

import unittest

from ..libs.normalizers import (
    clean_zipcode,
)


class ZipcodeTests(unittest.TestCase):
    def test_it_works(self):
        fixtures = (
            ('', ''),
            ('12345', '12345'),
            ('12345-1234', '12345-1234'),
            ('123456789', '12345-6789'),
            ('12345678a', '12345678a'),
            ('123456789a', '123456789a'),
        )
        for input, expected in fixtures:
            self.assertEqual(clean_zipcode(input), expected)
