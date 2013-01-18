from django.db.models import Sum
from django.test import TestCase


from tx_lobbying.factories import (InterestFactory, LobbyistFactory,
        LobbyistYearFactory,
        CompensationFactory)
from tx_lobbying.models import Interest


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
            Interest.objects.filter(compensation__year__lobbyist=lobbyist).distinct()

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
        lobbyist = LobbyistFactory.create()
        year = LobbyistYearFactory.create(lobbyist=lobbyist, year=2000)
        NUM_CLIENTS = 3
        for x in range(0, NUM_CLIENTS):
            CompensationFactory.create(year=year)

        try:
            # number of years of data we have for a lobbyist
            self.assertEqual(lobbyist.years.count(), 1)
            # number of clients a lobbyist had that year
            self.assertEqual(year.clients.count(), NUM_CLIENTS)
            self.assertEqual(year.compensation_set.count(), NUM_CLIENTS)
            # we can .annotate income onto the queryset
            for year in lobbyist.years.all().annotate(
                    income=Sum('compensation__amount_guess')):
                income = 0
                for compensation in year.compensation_set.all():
                    income += compensation.amount_guess
                self.assertEqual(income, year.income)

        except Exception as e:
            self.fail("Ha ha, %s" % e)
