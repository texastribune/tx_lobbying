import unittest

from ..scrapers.registration import update_or_create_interest, process_row


SAMPLE_ROW = {
    'ADDRESS1': u'303 Vale Street',
    'ADDRESS2': u'',
    'AMOUNT': u'$50,000 - $99,999.99',
    'CITY': u'Austin',
    'CLIENT_NUM': u'1',
    'COMPCODE': u'4',
    'CONCERNAME': u'Insperity',
    'EC_ADR1': u'19001 Crescent Springs Drive',
    'EC_ADR2': u'',
    'EC_CITY': u'Kingwood',
    'EC_STCD': u'TX',
    'EC_ZIP4': u'77339',
    'FILER_ID': u'00035415',
    'FIRM_NAML': u'',
    'I4E_NAML': u'',
    'LOBBYNAME': u'Alcorta III, Victor',
    'LOBPHON': u'(512) 657-4880',
    'LOSTART': u'2014-01-17',
    'LOTERM': u'2014-12-31',
    'NHIGH': u'99999.99',
    'NLOW': u'50000',
    'NORM_BUS': u'Attorney, Alcorta Law Firm PLLC',
    'REPNO': u'610177',
    'RPT_DATE': u'2014-04-08',
    'SOFTWARE_V': u'2.5.8',
    'SORTNAME': u'ALCORTA, VICTOR  III',
    'SOURCE': u'E',
    'STARTDT': u'2014-01-17',
    'STATE': u'TX',
    'TERMDATE': u'2014-12-31',
    'TYPECOPM': u'Prospective',
    'YEAR_APPL': u'2014',
    'ZIPCODE': u'78746',
}


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
        interest, address, created = update_or_create_interest(row)

        self.assertEqual(interest.name, 'Megacorp')
        self.assertEqual(interest.address.address1, '123 Fake')
        self.assertEqual(interest.address.address2, 'B')
        self.assertEqual(interest.address.city, 'C')
        self.assertEqual(interest.address.state, 'TX')
        self.assertEqual(interest.address.zipcode, '78701')
        # double check formatting
        self.assertEqual(unicode(interest.address), '123 Fake \nB \nC, TX 78701')

    def test_process_row_works(row):
        process_row(SAMPLE_ROW)
