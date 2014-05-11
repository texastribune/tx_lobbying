import unittest

from django.test import TestCase

from ..factories import CoversheetFactory
from ..models import Subject, SubjectMatterReport
from ..scrapers.registration import get_or_create_interest, process_row
from ..scrapers.expenses import _covers_inner, row_LaSub
from . import sample_rows


LOBCON_ROW = {
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

# LaCVR.csv
COVER_ROW = {
    'AWRD_MEMO': u'',
    'CORR_EXPL': u'',
    'CORR_NUM': u'0',
    'COR_AFF_CB': u'',
    'CVR_MEMO': u'',
    'DOCK_MEMO': u'',
    'DUE_DATE': u'1/11/1993',
    'ENTITY_CD': u'IND',
    'ENT_MEMO': u'',
    'EVNT_MEMO': u'',
    'EXBEN_EVNT': u'0',
    'EXBEN_EXEC': u'0',
    'EXBEN_FAM': u'0',
    'EXBEN_GUES': u'',
    'EXBEN_LEG': u'0',
    'EXBEN_OTH': u'0',
    'EXBEN_REP': u'0',
    'EXBEN_SEN': u'0',
    'EXTYP_AWDS': u'0',
    'EXTYP_ENT': u'0',
    'EXTYP_EVNT': u'0',
    'EXTYP_FOOD': u'0',
    'EXTYP_GIFT': u'0',
    'EXTYP_MEDA': u'0',
    'EXTYP_TRAN': u'0',
    'FILED_DATE': u'1/8/1993',
    'FILERSHORT': u'',
    'FILER_ID': u'00012705',
    'FILER_NAMF': u'',
    'FILER_NAML': u'',
    'FILER_NAMS': u'',
    'FILER_NAMT': u'',
    'FOOD_MEMO': u'',
    'GIFT_MEMO': u'',
    'HOWFILED': u'Paper',
    'IND4ENT_YN': u'',
    'LOBENDDT': u'12/31/1993',
    'LOBSTARTDT': u'1/1/1993',
    'LOB_NAME': u'Dabbs, Michael J.',
    'LOB_SORT': u'DABBS, MICHAEL J.',
    'RDL_APR_CB': u'',
    'RDL_AUG_CB': u'',
    'RDL_DEC_CB': u'',
    'RDL_FEB_CB': u'',
    'RDL_JAN_CB': u'',
    'RDL_JUL_CB': u'',
    'RDL_JUN_CB': u'',
    'RDL_MAR_CB': u'',
    'RDL_MAY_CB': u'',
    'RDL_NOV_CB': u'',
    'RDL_OCT_CB': u'',
    'RDL_SEP_CB': u'',
    'REPNO': u'4025',
    'RPT_BEG_DT': u'1/1/1992',
    'RPT_DATE': u'1/8/1993',
    'RPT_END_DT': u'12/31/1992',
    'RT_1K_CB': u'',
    'RT_FIN_CB': u'',
    'RT_MOD_CB': u'X',
    'RT_REG_CB': u'',
    'SIGN_PRINT': u'',
    'SUBJ_MEMO': u'',
    'TRAN_MEMO': u'',
    'YEAR_APPL': u'1993',
}


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
            process_row(LOBCON_ROW)


class ExpensesTest(TestCase):
    def test__covers_inner_works(self):
        _covers_inner(COVER_ROW)

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
