import datetime

import factory

from .models import (
    Interest,
    Lobbyist,
    ClientList,
)


class InterestFactory(factory.Factory):
    FACTORY_FOR = Interest

    name = factory.Sequence(lambda n: 'Interest {0}'.format(n))
    state = 'TX'


class LobbyistFactory(factory.Factory):
    FACTORY_FOR = Lobbyist
    filer_id = factory.Sequence(lambda n: n)
    sort_name = factory.Sequence(lambda n: 'Lobbyist {0}'.format(n))
    updated_at = factory.LazyAttribute(lambda a: datetime.date.today())


class ClientListFactory(factory.Factory):
    FACTORY_FOR = ClientList
    lobbyist = factory.SubFactory(LobbyistFactory)
    year = 2013
