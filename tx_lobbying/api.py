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

    def get_query_set(self, request, *args, **kwargs):
        # modified to add prefetch_related
        return self.model.objects.all().prefetch_related('stats')

    def serialize(self, objs):
        site = self.request.META.get('HTTP_HOST', '')  # not set on test client

        def collapse_stats_fixup(obj, data):
            """Condense total_spent stats into a simpler dict."""
            stats = data.pop('stats')
            data['total_spent'] = {x['year']: x['total_spent'] for x in stats}
            return data

        return serialize(
            objs,
            fields=(
                'filer_id',
                'name',
                ('url', lambda x: site + reverse(
                    'tx_lobbying:api:lobbyist_detail',
                    kwargs={'filer_id': x.filer_id}
                )),
            ),
            include=(
                ('stats', dict(
                    fields=(
                        'year',
                        'total_spent',
                    ),
                )),
            ),
            fixup=collapse_stats_fixup,
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
