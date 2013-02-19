from django.test import TestCase


from tx_lobbying.factories import (LobbyistFactory, ExpenseCoversheetFactory)
from tx_lobbying.models import LobbyistStat


class LobbyistTests(TestCase):
    def test_make_stats_is_accurate(self):
        lobbyist = LobbyistFactory.create()
        lobbyist.make_stats()
        self.assertEqual(lobbyist.stats.count(), 0)

        ExpenseCoversheetFactory.create(lobbyist=lobbyist,
            year=2000, spent_guess="100")
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
