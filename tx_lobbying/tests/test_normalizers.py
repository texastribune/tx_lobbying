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
    def test_concatenation_works(self):
        fixtures = (
            ('123 Fake Street', '', '123 Fake ST'),
            (' 123 Fake Street ', ' ', '123 Fake ST'),
        )
        for addr1, addr2, expected in fixtures:
            self.assertEqual(clean_street(addr1, addr2), expected)

    def test_it_works(self):
        fixtures = (
            ('1001 Congress Avenue Suite 450', '1001 Congress AVE STE 450'),
            ('1001 Congress Ste 200', '1001 Congress STE 200'),
            ('1001 G Street NW #400-E', '1001 G ST NW # 400-E'),
            ('1001 Pennsylvania Ave NW Suite 710', '1001 Pennsylvania AVE NW STE 710'),
            ('1005 Congress Ave Ste 1000B', '1005 Congress AVE STE 1000B'),
            ('101 East Gillis PO Box 677', '101 E Gillis PO Box 677'),
            ('101 Parklane Boulevard Suite 301', '101 Parklane BLVD STE 301'),
            ('901 E Street NW 10th Floor', '901 E ST NW 10th FL'),
            ('1000 Louisiana ST. STE 5600', '1000 Louisiana ST STE 5600'),
            ('1000 S. Beckham', '1000 S Beckham'),
            # TODO
            # ('P O Box 7230', 'PO Box 7230'),
        )
        for addr1, expected in fixtures:
            self.assertEqual(clean_street(addr1), expected)

    def test_care_of(self):
        fixtures = (
            ('', '', ''),
            ('c/o Dude', 'PO Box 123', 'PO Box 123'),
            ('C/O Dude', 'PO Box 123', 'PO Box 123'),
        )
        for addr1, addr2, expected in fixtures:
            self.assertEqual(clean_street(addr1, addr2), expected)
