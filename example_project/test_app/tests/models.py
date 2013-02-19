from django.test import TestCase


from tx_lobbying.factories import (LobbyistFactory, ExpenseCoversheetFactory)
from tx_lobbying.models import LobbyistStat


class LobbyistTests(TestCase):
    def test_make_stats_is_accurate(self):
        lobbyist = LobbyistFactory.create()
        lobbyist.make_stats()
        self.assertEqual(lobbyist.stats.count(), 0)

        print ExpenseCoversheetFactory.create()
        lobbyist.make_stats()
