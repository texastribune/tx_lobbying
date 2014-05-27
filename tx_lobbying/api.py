from restless.views import Endpoint
from restless.models import serialize

from . import models


address_data = dict(
    include=(
        ('name', lambda x: unicode(x)),
    ),
)


class GetLobbyistData(Endpoint):
    def get(self, request, filer_id):
        obj = models.Lobbyist.objects.get(filer_id=filer_id)
        return serialize(
            obj,
            fields=[
                'id',
                'name',
                ('address', address_data),
            ],
            include=(
                ('years', dict(
                    fields=(
                        'year',
                        ('clients', dict(
                            include=(
                                ('address', address_data),
                            ),
                            exclude=(
                                'nomenklatura_id',
                            ),
                        )),
                    )
                )),
            )
        )
