from django.db.models import Sum
from django.test import TestCase


from tx_lobbying.factories import (InterestFactory, LobbyistFactory,
        ClientListFactory,
        CompensationFactory)


class NamedPoorlyTestCase(TestCase):
    def test_model_relations_api(self):
        """Test the calls used to move between the relations for the models."""
        i = InterestFactory.create()
        l = LobbyistFactory.create()

        try:
            # add an `Interest` to a `Lobbyist`
            c = ClientListFactory.create(lobbyist=l, year=2000)
            CompensationFactory.create(clientlist=c, interest=i,
                updated_at=l.updated_at)

            # get all the `Interests` for a `Lobbyist`
            for c in l.clientlist_set.all():
                c.clients.all()

            # get all the `Interests` for a `Lobbyist` for a year
            l.clientlist_set.get(year=2000).clients.all()

            # get all the `Lobbyist`s for an `Interest`
            i.clientlist_set.all().values('lobbyist')

            # get all the `Lobbyist`s for an `Interest` for a year
            i.clientlist_set.filter(year=2000).values('lobbyist')

        except Exception as e:
            self.fail("Ha ha, %s" % e)

    def test_lobbyist_compensation_relation_api(self):
        l = LobbyistFactory.create()
        c = ClientListFactory.create(lobbyist=l, year=2000)
        NUM_CLIENTS = 3
        for x in range(0, NUM_CLIENTS):
            CompensationFactory.create(clientlist=c)

        try:
            self.assertEqual(l.clientlist_set.count(), 1)
            self.assertEqual(c.clients.count(), NUM_CLIENTS)
            self.assertEqual(c.compensation_set.count(), NUM_CLIENTS)
            for c in l.clientlist_set.all().annotate(
                    income=Sum('compensation__amount_guess')):
                income = 0
                for compensation in c.compensation_set.all():
                    income += compensation.amount_guess
                self.assertEqual(income, c.income)

        except Exception as e:
            self.fail("Ha ha, %s" % e)
