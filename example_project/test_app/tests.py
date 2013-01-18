from django.test import TestCase


from tx_lobbying.factories import (InterestFactory, LobbyistFactory, ClientListFactory)


class NamedPoorlyTestCase(TestCase):
    def test_model_relations_api(self):
        """Test the calls used to move between the relations for the models."""
        i = InterestFactory.create()
        l = LobbyistFactory.create()

        try:
            # add an `Interest` to a `Lobbyist`
            c = ClientListFactory.create(lobbyist=l, year=2000)
            c.clients.add(i)

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
