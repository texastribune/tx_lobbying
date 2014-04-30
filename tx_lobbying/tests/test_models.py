import random

from django.db.models import Sum
from django.test import TestCase

from tx_lobbying.factories import (
    InterestFactory,
    LobbyistFactory,
    LobbyistYearFactory,
    ExpenseCoversheetFactory,
    CompensationFactory,
)
from tx_lobbying.models import (Interest, InterestStats, Lobbyist,
    LobbyistYear, )


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

        # associate N `Lobbyist`s with it through `LobbyistYear`
        for i in range(N):
            year = LobbyistYearFactory.create(year=self.year)
            CompensationFactory.create(year=year, interest=self.interest,
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

        # associate N `Lobbyist`s with it through `LobbyistYear`
        for i in range(N):
            year = LobbyistYearFactory.create(year=self.year)
            CompensationFactory.create(year=year, interest=self.interest,
                amount_guess=i, amount_high=i * 2, amount_low=0)
        self.interest.make_stats_for_year(self.year)

        # attempt to poison stats with extra data
        for i in range(N)[::2]:
            year = LobbyistYearFactory.create(year=self.year + 1)
            CompensationFactory.create(year=year, interest=self.interest)
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

        # associate num_lobbyists `Lobbyist`s with it through `LobbyistYear`
        for i in range(num_lobbyists):
            year = LobbyistYearFactory.create(year=self.year)
            interest = Interest.objects.all().order_by('?')[0]
            CompensationFactory.create(year=year, interest=interest,
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

    def test_make_stats_finds_all_years(self):
        year2000 = LobbyistYearFactory.create(year=2000)
        CompensationFactory.create(year=year2000, interest=self.interest,
            amount_low=2000, amount_guess=2000, amount_high=2000)
        year2001 = LobbyistYearFactory.create(year=2001)
        CompensationFactory.create(year=year2001, interest=self.interest,
            amount_low=2001, amount_guess=2001, amount_high=2001)
        year2004 = LobbyistYearFactory.create(year=2004)
        CompensationFactory.create(year=year2004, interest=self.interest,
            amount_low=2004, amount_guess=2004, amount_high=2004)
        self.interest.make_stats()
        # assert stats are generated
        self.assertFalse(self.interest.stats.filter(year=1999).exists())
        self.assertTrue(self.interest.stats.filter(year=2000).exists())
        self.assertTrue(self.interest.stats.filter(year=2001).exists())
        self.assertTrue(self.interest.stats.filter(year=2002).exists())
        self.assertTrue(self.interest.stats.filter(year=2003).exists())
        self.assertTrue(self.interest.stats.filter(year=2004).exists())
        self.assertFalse(self.interest.stats.filter(year=2005).exists())
        # document that stats for empty year are None
        stat = self.interest.stats.get(year=2002)
        self.assertEqual(stat.low, None)
        self.assertEqual(stat.guess, None)
        self.assertEqual(stat.high, None)


class LobbyistTest(TestCase):
    def test_make_stats_is_accurate(self):
        lobbyist = LobbyistFactory()
        lobbyist.make_stats()
        self.assertEqual(lobbyist.stats.count(), 0)

        ExpenseCoversheetFactory(
            lobbyist=lobbyist, year=2000, spent_guess=100)
        lobbyist.make_stats()
        self.assertEqual(lobbyist.stats.count(), 1)
        self.assertEqual(lobbyist.stats.get(year=2000).spent, 100)

        ExpenseCoversheetFactory.create(lobbyist=lobbyist,
            year=2000, spent_guess="200")
        lobbyist.make_stats()
        self.assertEqual(lobbyist.stats.count(), 1)
        self.assertEqual(lobbyist.stats.get(year=2000).spent, 300)

        ExpenseCoversheetFactory.create(lobbyist=lobbyist,
            year=2001, spent_guess="400")
        lobbyist.make_stats()
        self.assertEqual(lobbyist.stats.count(), 2)
        self.assertEqual(lobbyist.stats.get(year=2000).spent, 300)
        self.assertEqual(lobbyist.stats.get(year=2001).spent, 400)


class NamedPoorlyTestCase(TestCase):
    def test_model_relations_api(self):
        """Test the calls used to move between the relations for the models."""
        i = InterestFactory.create()
        lobbyist = LobbyistFactory.create()
        YEAR = 2000

        try:
            # add an `Interest` to a `Lobbyist`
            year = LobbyistYearFactory.create(lobbyist=lobbyist, year=YEAR)
            CompensationFactory.create(year=year, interest=i)

            # get all the `Interest`s for a `Lobbyist`
            Interest.objects.filter(compensation__year__lobbyist=lobbyist)

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
        year = LobbyistYearFactory.create(lobbyist=lobbyist)
        for x in range(0, NUM_CLIENTS):
            CompensationFactory.create(year=year)

        try:
            # number of years of data we have for a lobbyist
            self.assertEqual(lobbyist.years.count(), 1)
            # number of clients a lobbyist had that year
            self.assertEqual(year.clients.count(), NUM_CLIENTS)
            self.assertEqual(year.compensation_set.count(), NUM_CLIENTS)
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
            year = LobbyistYearFactory.create(lobbyist=lobbyist, year=YEAR)
            for x in range(0, NUM_CLIENTS):
                CompensationFactory.create(year=year)

        # Here's a queryset to get the best paid `Lobbyist`s in a year
        qs = LobbyistYear.objects.filter(year=YEAR).annotate(
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
                year = LobbyistYear.objects.get(lobbyist=lobbyist, year=YEAR)
            except LobbyistYear.DoesNotExist:
                year = LobbyistYearFactory.create(lobbyist=lobbyist, year=YEAR)
            CompensationFactory.create(year=year, interest=i)
            # denormalize interest stats
            i.make_stats_for_year(YEAR)

        # use `__exact`, django ORM attempts to evaluate __year as a date lookup
        for stat in InterestStats.objects.filter(year__exact=YEAR).order_by(
                '-guess'):
            # print stat
            stat
