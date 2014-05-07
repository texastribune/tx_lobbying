import unittest

from address_normalizer import (
    clean_zipcode,
)


class Test_clean_zipcode(unittest.TestCase):
    def test_it_works(self):
        fixture = (
            ('', ''),
            ('12345', '12345'),
            ('12345-1234', '12345-1234'),
            ('123456789', '12345-6789'),
        )
        for input, expected in fixture:
            self.assertEqual(clean_zipcode(input), expected)

