import datetime
import random

import factory
import names

from . import models
from .models import (
    Interest,
    Lobbyist,
    LobbyistYear,
    Compensation,
    ExpenseCoversheet,
)


class AddressFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Address
    state = u'TX'


class InterestFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Interest

    name = factory.Sequence(lambda n: 'Interest {0}'.format(n))
    address = factory.SubFactory(AddressFactory)


class LobbyistFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Lobbyist
    filer_id = factory.Sequence(lambda n: n)
    first_name = factory.LazyAttribute(lambda a: names.get_first_name())
    last_name = factory.LazyAttribute(lambda a: names.get_last_name())
    sort_name = factory.LazyAttribute(lambda a: "%s %s" % (
        a.last_name, a.first_name))
    updated_at = factory.LazyAttribute(lambda a: datetime.date.today())


class LobbyistYearFactory(factory.DjangoModelFactory):
    FACTORY_FOR = LobbyistYear
    lobbyist = factory.SubFactory(LobbyistFactory)
    year = 2013


class CompensationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Compensation
    amount_high = factory.LazyAttribute(lambda a: random.randint(10000, 100000))
    amount_low = factory.LazyAttribute(lambda a: random.randint(0, a.amount_high))
    amount_guess = factory.LazyAttribute(lambda a: (a.amount_high + a.amount_low) / 2)
    annum = factory.SubFactory(LobbyistYearFactory)
    interest = factory.SubFactory(InterestFactory)
    updated_at = factory.LazyAttribute(lambda a: datetime.date.today())


class ExpenseCoversheetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ExpenseCoversheet
    lobbyist = factory.SubFactory(LobbyistFactory)
    report_date = '2001-04-01'
    report_id = factory.Sequence(lambda n: n)
    year = '2001'
    spent_guess = factory.LazyAttribute(lambda a: random.randint(10000, 100000))
