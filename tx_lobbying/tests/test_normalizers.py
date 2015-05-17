from __future__ import unicode_literals

import unittest

from ..libs.normalizers import (
    clean_zipcode,
    clean_street,
)


class ZipcodeTests(unittest.TestCase):
    def test_it_works(self):
        fixtures = (
            ('', ''),
            ('12345', '12345'),
            ('12345-1234', '12345'),
            ('123456789', '12345'),
            ('12345678a', '12345678a'),
            ('123456789a', '123456789a'),
        )
        for input, expected in fixtures:
            self.assertEqual(clean_zipcode(input), expected)


class AddressTests(unittest.TestCase):
    def test_it_works(self):
        fixtures = (
            ('123 Fake Street', '', '123 Fake Street'),
            (' 123 Fake Street ', ' ', '123 Fake Street'),
            ('123 Fake Street', 'Suite 1', '123 Fake Street Suite 1'),
            ('123  Fake  Street', 'Suite 1', '123 Fake Street Suite 1'),
            ('123 Fake Street.', 'Suite. 1', '123 Fake Street Suite 1'),
        )
        for addr1, addr2, expected in fixtures:
            self.assertEqual(clean_street(addr1, addr2), expected)

    def test_care_of(self):
        fixtures = (
            ('', '', ''),
            ('c/o Dude', 'PO Box 123', 'PO Box 123'),
            ('C/O Dude', 'PO Box 123', 'PO Box 123'),
        )
        for addr1, addr2, expected in fixtures:
            self.assertEqual(clean_street(addr1, addr2), expected)
