import unittest

from django.test import TestCase

from ..factories import CoversheetFactory
from ..models import Subject, SubjectMatterReport
from ..scrapers.registration import get_or_create_interest, process_row
from ..scrapers.expenses import _covers_inner, row_LaSub
from . import sample_rows


class RegistrationTest(TestCase):
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
        with self.assertNumQueries(8):
            interest, address, created = get_or_create_interest(row)

        self.assertEqual(interest.name, 'Megacorp')
        self.assertEqual(interest.address.address1, '123 Fake')
        self.assertEqual(interest.address.address2, 'B')
        self.assertEqual(interest.address.city, 'C')
        self.assertEqual(interest.address.state, 'TX')
        self.assertEqual(interest.address.zipcode, '78701')
        # double check formatting
        self.assertEqual(unicode(interest.address), '123 Fake \nB \nC, TX 78701')

    def test_process_row_works(self):
        with self.assertNumQueries(28):
            process_row(sample_rows.LOBCON)


class ExpensesTest(TestCase):
    def test__covers_inner_works(self):
        _covers_inner(sample_rows.COVER)

    def test_row_LaSub(self):
        row = sample_rows.LASUB
        # requires pre-existing coversheet
        cover = CoversheetFactory(report_id=row['REPNO'])

        with self.assertNumQueries(11):
            row_LaSub(row)
        subject = Subject.objects.get(category_id=row['CATGNUM'])
        report = SubjectMatterReport.objects.get(cover=cover)
        self.assertTrue(subject)
        self.assertTrue(report)

        # assert re-running uses fewer queries
        with self.assertNumQueries(7):
            row_LaSub(row)

        # assert a new report wasn't made
        self.assertEqual(1, Subject.objects.count())
        self.assertEqual(1, SubjectMatterReport.objects.count())

        # make a new subject
        row2 = dict(row, CATGNUM=84)
        with self.assertNumQueries(11):
            row_LaSub(row2)
        self.assertEqual(2, Subject.objects.count())
        self.assertEqual(1, SubjectMatterReport.objects.count())
