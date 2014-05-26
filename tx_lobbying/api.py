from restless.views import Endpoint
from restless.models import serialize

from . import models


class GetLobbyistData(Endpoint):
    def get(self, request, filer_id):
        obj = models.Lobbyist.objects.get(filer_id=filer_id)
        return serialize(obj)
