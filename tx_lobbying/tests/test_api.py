from django.core.urlresolvers import reverse
from django.test import TestCase

from ..factories import LobbyistFactory


class UrlsTest(TestCase):
    """
    Just make sure these endpoints are listening.
    """
    def test_lobbyist(self):
        lobbyist = LobbyistFactory()
        url = reverse('tx_lobbying:api:lobbyist_detail',
            kwargs={'filer_id': lobbyist.filer_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
