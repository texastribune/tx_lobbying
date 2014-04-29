import unittest

from ..scrapers.registration import update_or_create_interest


class RegistrationTest(unittest.TestCase):
    """
    Tests surrounding getting data from LobConXX.csv

    Columns:

        FILER_ID,
        REPNO,
        CLIENT_NUM,
        LOBBYNAME,
        NORM_BUS,
        ADDRESS1,
        ADDRESS2,
        CITY,
        STATE,
        ZIPCODE,
        LOBPHON,
        LOSTART,
        LOTERM,
        CONCERNAME,
        EC_ADR1,
        EC_ADR2,
        EC_CITY,
        EC_STCD,
        EC_ZIP4,
        STARTDT,
        TERMDATE,
        TYPECOPM,
        COMPCODE,
        AMOUNT,
        NLOW,
        NHIGH,
        SORTNAME,
        FIRM_NAML,
        I4E_NAML,
        RPT_DATE,
        SOURCE,
        SOFTWARE_V,
        YEAR_APPL
    """
    def test_update_or_create_interest_works(self):
        row = {
            'CONCERNAME': 'Megacorp',
            'EC_ADR1': '123 Fake',
            'EC_ADR2': 'B',
            'EC_CITY': 'C',
            'EC_STCD': 'TX',
            'EC_ZIP4': '78701',
        }
        interest, created = update_or_create_interest(row)

        self.assertEqual(interest.name, 'Megacorp')
        self.assertEqual(interest.address1, '123 Fake')
        self.assertEqual(interest.address2, 'B')
        self.assertEqual(interest.city, 'C')
        self.assertEqual(interest.state, 'TX')
        self.assertEqual(interest.zipcode, '78701')
        # double check formatting
        self.assertEqual(interest.address, '123 Fake \nB \nC, TX 78701')
