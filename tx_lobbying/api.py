from restless.models import serialize
from restless.modelviews import DetailEndpoint

from . import models


address_data = dict(
    include=(
        ('name', lambda x: unicode(x)),
    ),
)


class LobbyistDetail(DetailEndpoint):
    lookup_field = 'filer_id'
    model = models.Lobbyist

    def serialize(self, obj):
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
