from django.core.urlresolvers import reverse
from restless.models import serialize
from restless.modelviews import ListEndpoint, DetailEndpoint

from . import models


address_data = dict(
    include=(
        ('name', lambda x: unicode(x)),
    ),
)


class LobbyistList(ListEndpoint):
    model = models.Lobbyist

    def serialize(self, objs):
        site = self.request.META.get('HTTP_HOST', '')  # not set on test client
        return serialize(
            objs,
            fields=(
                'filer_id',
                'name',
                ('url', lambda x: site + reverse(
                    'tx_lobbying:api:lobbyist_detail',
                    kwargs={'filer_id': x.filer_id}
                )),
                # TODO years this lobbyist was active and how much was spent
            )
        )


class LobbyistDetail(DetailEndpoint):
    lookup_field = 'filer_id'
    model = models.Lobbyist

    def serialize(self, obj):
        return serialize(
            obj,
            fields=(
                'id',
                'name',
                ('address', address_data),
            ),
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
