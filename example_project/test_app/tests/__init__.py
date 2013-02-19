from django.db.models import Sum
from django.test import TestCase


from tx_lobbying.factories import (InterestFactory, LobbyistFactory,
        LobbyistYearFactory,
        CompensationFactory)
from tx_lobbying.models import (Interest, InterestStats, Lobbyist,
    LobbyistYear, )


from .models import *


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


class UtilsTests(TestCase):
    def test_intereststats_are_accurate(self):
        """Make sure the `Interest` data denormalization is accurate."""
        YEAR = 2000
        N = 10

        # make one `Interest`
        interest = InterestFactory.create()

        # associate N `Lobbyist`s with it through `LobbyistYear`
        for i in range(N):
            year = LobbyistYearFactory.create(year=YEAR)
            CompensationFactory.create(year=year, interest=interest,
                amount_guess=i, amount_high=i * 2, amount_low=0)
        interest.make_stats_for_year(YEAR)

        # attempt to poison stats with extra data
        for i in range(N)[::2]:
            year = LobbyistYearFactory.create(year=YEAR + 1)
            CompensationFactory.create(year=year, interest=interest)
        interest.make_stats_for_year(YEAR + 1)

        stat = interest.stats.all().get(year=YEAR)
        self.assertEqual(stat.guess, N * (N - 1) / 2)  # math!
        self.assertEqual(stat.high, N * (N - 1))
        self.assertEqual(stat.low, 0)
        # print interest.stats.all().get(year=YEAR + 1)
