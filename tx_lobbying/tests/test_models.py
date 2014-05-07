import random

from django.db.models import Sum
from django.test import TestCase

from tx_lobbying.factories import (
    AddressFactory,
    InterestFactory,
    LobbyistFactory,
    LobbyistAnnumFactory,
    RegistrationReportFactory,
    CoversheetFactory,
    CompensationFactory,
)
from tx_lobbying.models import (Address, Interest, InterestStats, Lobbyist,
    LobbyistAnnum, RegistrationReport, )


class InterestTest(TestCase):
    def setUp(self):
        self.interest = InterestFactory()
        self.year = 2000

    def test_canonical_field_works(self):
        a1 = InterestFactory(canonical=self.interest)
        self.assertIn(a1, self.interest.aliases.all())

    def test_compensation_set_massive_works_the_same_way(self):
        comp = CompensationFactory(interest=self.interest)
        with self.assertNumQueries(1):
            self.assertIn(comp, self.interest.compensation_set.all())
        with self.assertNumQueries(1):
            self.assertIn(comp, self.interest.compensation_set_massive.all())

    def test_compensation_set_massive_works(self):
        c1 = CompensationFactory(interest=self.interest)
        c2 = CompensationFactory(interest__canonical=self.interest)
        self.assertIn(c1, self.interest.compensation_set.all())
        self.assertNotIn(c2, self.interest.compensation_set.all())
        self.assertIn(c2, self.interest.compensation_set_massive)

    def test_make_stats_for_year_is_accurate(self):
        N = 10

        # associate N `Lobbyist`s with it through `LobbyistAnnum`
        for i in range(N):
            annum = LobbyistAnnumFactory.create(year=self.year)
            CompensationFactory.create(annum=annum, interest=self.interest,
                amount_guess=i, amount_high=i * 2, amount_low=0)
        with self.assertNumQueries(5):
            # 1 to get the stats
            # 1 to GET
            # 1 to INSERT
            # 2 for transaction management
            self.interest.make_stats_for_year(self.year)

        stat = self.interest.stats.all().get(year=self.year)
        self.assertEqual(stat.guess, N * (N - 1) / 2)  # math!
        self.assertEqual(stat.high, N * (N - 1))
        self.assertEqual(stat.low, 0)

    def test_make_stats_for_year_does_not_pick_up_other_years(self):
        N = 10

        # associate N `Lobbyist`s with it through `LobbyistAnnum`
        for i in range(N):
            annum = LobbyistAnnumFactory.create(year=self.year)
            CompensationFactory.create(annum=annum, interest=self.interest,
                amount_guess=i, amount_high=i * 2, amount_low=0)
        self.interest.make_stats_for_year(self.year)

        # attempt to poison stats with extra data
        for i in range(N)[::2]:
            annum = LobbyistAnnumFactory.create(year=self.year + 1)
            CompensationFactory.create(annum=annum, interest=self.interest)
        self.interest.make_stats_for_year(self.year + 1)

        stat = self.interest.stats.all().get(year=self.year)
        self.assertEqual(stat.guess, N * (N - 1) / 2)  # math!
        self.assertEqual(stat.high, N * (N - 1))
        self.assertEqual(stat.low, 0)

    def test_make_stats_for_year_takes_aliases_into_account(self):
        """
        This is just like test_make_stats_for_year_is_accurate, except we
        spread the lobbyists to a pool of interests that are all really the
        same interest.
        """
        num_lobbyists = random.randint(7, 13)
        num_interests = random.randint(2, 3)

        # assert we started off with 1 `Interest` (self.interest)
        self.assertEqual(Interest.objects.count(), 1)
        for i in range(num_interests):
            InterestFactory(canonical=self.interest)
        # sanity check
        self.assertEqual(self.interest.aliases.count(), num_interests)

        # associate num_lobbyists `Lobbyist`s with it through `LobbyistAnnum`
        for i in range(num_lobbyists):
            year = LobbyistAnnumFactory.create(year=self.year)
            interest = Interest.objects.all().order_by('?')[0]
            CompensationFactory(annum=year, interest=interest,
                amount_guess=i, amount_high=i * 2, amount_low=0)
        with self.assertNumQueries(5):
            # 1 to get the stats
            # 1 to GET
            # 1 to INSERT
            # 2 for transaction management
            self.interest.make_stats_for_year(self.year)

        stat = self.interest.stats.all().get(year=self.year)
        self.assertEqual(stat.guess, num_lobbyists * (num_lobbyists - 1) / 2)  # math!
        self.assertEqual(stat.high, num_lobbyists * (num_lobbyists - 1))
        self.assertEqual(stat.low, 0)

    def test_make_stats_for_year_does_nothing_for_noncanonical_interests(self):
        interest = InterestFactory(canonical=self.interest)
        year2000 = LobbyistAnnumFactory.create(year=2000)
        CompensationFactory(annum=year2000, interest=interest,
            amount_low=2000, amount_guess=2000, amount_high=2000)
        interest.make_stats_for_year(2000)
        # assert noncanonical interest did not have stats generated
        self.assertEqual(0, interest.stats.count())
        # assert canonical interest got the stats instead
        self.assertEqual(1, self.interest.stats.count())

    def test_make_stats_finds_all_years(self):
        year2000 = LobbyistAnnumFactory.create(year=2000)
        CompensationFactory(annum=year2000, interest=self.interest,
            amount_low=2000, amount_guess=2000, amount_high=2000)
        year2000b = LobbyistAnnumFactory.create(year=2000)
        CompensationFactory(annum=year2000b, interest=self.interest,
            amount_low=2000, amount_guess=2000, amount_high=2000)
        year2001 = LobbyistAnnumFactory.create(year=2001)
        CompensationFactory(annum=year2001, interest=self.interest,
            amount_low=2001, amount_guess=2001, amount_high=2001)
        year2004 = LobbyistAnnumFactory.create(year=2004)
        CompensationFactory(annum=year2004, interest=self.interest,
            amount_low=2004, amount_guess=2004, amount_high=2004)
        with self.assertNumQueries(19):
            self.interest.make_stats()
        # assert stats are generated
        self.assertFalse(self.interest.stats.filter(year=1999).exists())
        self.assertTrue(self.interest.stats.filter(year=2000).exists())
        self.assertTrue(self.interest.stats.filter(year=2001).exists())
        self.assertFalse(self.interest.stats.filter(year=2002).exists())
        self.assertFalse(self.interest.stats.filter(year=2003).exists())
        self.assertTrue(self.interest.stats.filter(year=2004).exists())
        self.assertFalse(self.interest.stats.filter(year=2005).exists())

    def test_get_all_addresses_works(self):
        a1 = AddressFactory()
        a2 = AddressFactory()
        CompensationFactory(interest=self.interest, address=a1)
        CompensationFactory(interest=self.interest, address=a2)
        addresses = self.interest.get_all_addresses()
        self.assertIn(a1, addresses)
        self.assertIn(a2, addresses)
        # property version too
        self.assertIn(a1, self.interest.address_set)
        self.assertIn(a2, self.interest.address_set)

    def test_get_all_addresses_is_distinct(self):
        a1 = AddressFactory()
        CompensationFactory(interest=self.interest, address=a1)
        CompensationFactory(interest=self.interest, address=a1)
        addresses = self.interest.get_all_addresses()
        self.assertEqual(addresses.count(), 1)

    def test_get_all_addresses_can_get_aliases(self):
        interest = InterestFactory(canonical=self.interest)
        a1 = AddressFactory()
        a2 = AddressFactory()
        CompensationFactory(interest=self.interest, address=a1)
        CompensationFactory(interest=interest, address=a2)
        addresses = self.interest.get_all_addresses(include_aliases=True)
        self.assertIn(a1, addresses)
        self.assertIn(a2, addresses)
        # property version too
        self.assertIn(a1, self.interest.address_set_massive)
        self.assertNotIn(a2, self.interest.address_set)
        self.assertIn(a2, self.interest.address_set_massive)


class LobbyistTest(TestCase):
    def setUp(self):
        self.lobbyist = LobbyistFactory()

    def test_address_history_trivial_case_starts_is_empty(self):
        history = self.lobbyist.get_address_history()
        self.assertEqual(len(history), 0)

    def test_address_history_works_simple(self):
        RegistrationReportFactory(lobbyist=self.lobbyist)
        history = self.lobbyist.get_address_history()
        self.assertEqual(len(history), 1)
        entry = history[0]
        self.assertIsInstance(entry.address, Address)
        self.assertIsInstance(entry[0], Address)
        self.assertIsInstance(entry.registration, RegistrationReport)
        self.assertIsInstance(entry[1], RegistrationReport)

    def test_address_history_works_advanced(self):
        a1 = AddressFactory()
        a2 = AddressFactory()
        a3 = AddressFactory()
        RegistrationReportFactory(lobbyist=self.lobbyist, address=a1, year=2000)
        RegistrationReportFactory(lobbyist=self.lobbyist, address=a3, year=2002)
        RegistrationReportFactory(lobbyist=self.lobbyist, address=a3, year=2001)
        RegistrationReportFactory(lobbyist=self.lobbyist, address=a2, year=2003)
        history = self.lobbyist.get_address_history()
        # assert handles repeated address by collapsing it
        self.assertEqual(len(history), 3)
        # assert pulls address in chronological order
        self.assertEqual(history[0].address, a1)
        self.assertEqual(history[1].address, a3)
        self.assertEqual(history[2].address, a2)

    def test_make_stats_does_nothing_with_no_coversheets(self):
        self.assertEqual(self.lobbyist.coversheets.count(), 0)
        self.lobbyist.make_stats()
        self.assertEqual(self.lobbyist.stats.count(), 0)

    def test_make_stats_is_accurate(self):
        CoversheetFactory(
            lobbyist=self.lobbyist, year=2000, spent_guess=100)
        self.lobbyist.make_stats()
        self.assertEqual(self.lobbyist.stats.count(), 1)
        self.assertEqual(self.lobbyist.stats.get(year=2000).spent_guess, 100)

        CoversheetFactory.create(lobbyist=self.lobbyist,
            year=2000, spent_guess=200)
        self.lobbyist.make_stats()
        self.assertEqual(self.lobbyist.stats.count(), 1)
        self.assertEqual(self.lobbyist.stats.get(year=2000).spent_guess, 300)

        CoversheetFactory.create(lobbyist=self.lobbyist,
            year=2001, spent_guess=400, transportation=1)
        self.lobbyist.make_stats()
        self.assertEqual(self.lobbyist.stats.count(), 2)
        self.assertEqual(self.lobbyist.stats.get(year=2000).spent_guess, 300)
        self.assertEqual(self.lobbyist.stats.get(year=2001).spent_guess, 400)
        self.assertEqual(self.lobbyist.stats.get(year=2001).transportation, 1)


class NamedPoorlyTestCase(TestCase):
    def test_model_relations_api(self):
        """Test the calls used to move between the relations for the models."""
        i = InterestFactory()
        lobbyist = LobbyistFactory.create()
        YEAR = 2000

        try:
            # add an `Interest` to a `Lobbyist`
            annum = LobbyistAnnumFactory.create(lobbyist=lobbyist, year=YEAR)
            CompensationFactory.create(annum=annum, interest=i)

            # get all the `Interest`s for a `Lobbyist`
            Interest.objects.filter(compensation__annum__lobbyist=lobbyist)

            # get all the `Interest`s for a `Lobbyist` by year
            for year in lobbyist.years.all():
                year.clients.all()

            # get all the `Interest`s for a `Lobbyist` for a year
            lobbyist.years.get(year=YEAR).clients.all()

            # get all the `Lobbyist`s for an `Interest`
            i.years_available.all().values('lobbyist')

            # get all the `Lobbyist`s for an `Interest` for a year
            i.years_available.filter(year=YEAR).values('lobbyist')

        except Exception as e:
            self.fail("Ha ha, %s" % e)

    def test_lobbyist_compensation_relation_api(self):
        """More tests about getting between `Lobbyist`s and `Compensation`."""
        # Make a `Lobbyist` with NUM_CLIENTS clients.
        NUM_CLIENTS = 3
        lobbyist = LobbyistFactory.create()
        annum = LobbyistAnnumFactory.create(lobbyist=lobbyist)
        for x in range(0, NUM_CLIENTS):
            CompensationFactory(annum=annum)

        try:
            # number of years of data we have for a lobbyist
            self.assertEqual(lobbyist.years.count(), 1)
            # number of clients a lobbyist had that year
            self.assertEqual(annum.clients.count(), NUM_CLIENTS)
            self.assertEqual(annum.compensation_set.count(), NUM_CLIENTS)
            # make sure we can .annotate income onto the queryset
            for year in lobbyist.years.all().annotate(
                    income=Sum('compensation__amount_guess')):
                income = 0
                for compensation in year.compensation_set.all():
                    income += compensation.amount_guess
                self.assertEqual(income, year.income)

        except Exception as e:
            self.fail("Ha ha, %s" % e)

    def test_lobbyist_compensation_report_queryset(self):
        """Get a list of `Lobbyist`s sorted by their paycheck."""
        NUM_CLIENTS = 3
        YEAR = 2000

        for i in range(10):
            lobbyist = LobbyistFactory.create()
            annum = LobbyistAnnumFactory.create(lobbyist=lobbyist, year=YEAR)
            for x in range(0, NUM_CLIENTS):
                CompensationFactory(annum=annum)

        # Here's a queryset to get the best paid `Lobbyist`s in a year
        qs = LobbyistAnnum.objects.filter(year=YEAR).annotate(
            income=Sum('compensation__amount_guess')).order_by('-income')
        for year in qs:
            # print year.lobbyist, year.income
            year

    def test_interest_compensation_report_queryset(self):
        """Get a list of `Interest`s sorted by their bankroll of `Lobbyist`s."""
        YEAR = 2000

        for i in range(10):
            LobbyistFactory.create()
            InterestFactory.create()
            InterestFactory.create()

        for i in Interest.objects.all():
            lobbyist = Lobbyist.objects.all().order_by('?')[0]
            try:
                annum = LobbyistAnnum.objects.get(lobbyist=lobbyist, year=YEAR)
            except LobbyistAnnum.DoesNotExist:
                annum = LobbyistAnnumFactory.create(lobbyist=lobbyist, year=YEAR)
            CompensationFactory(annum=annum, interest=i)
            # denormalize interest stats
            i.make_stats_for_year(YEAR)

        # use `__exact`, django ORM attempts to evaluate __year as a date lookup
        for stat in InterestStats.objects.filter(year__exact=YEAR).order_by(
                '-guess'):
            # print stat
            stat
