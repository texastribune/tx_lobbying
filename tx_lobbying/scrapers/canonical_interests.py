"""
TODO change print to logger
"""
import logging
import os

from tx_lobbying.models import Interest
from tx_lobbying.scrapers.utils import DictReader


logger = logging.getLogger(__name__)


def set_canonical(interest, canonical):
    interest.stats.all().delete()
    if canonical:
        canonical.stats.all().delete()
    if interest.canonical:
        interest.canonical.stats.all().delete()
    interest.canonical = canonical
    interest.save(update_fields=('canonical', ))


def go(path):
    if not os.path.isfile(path):
        exit('Make sure you ran `make nomenklatura` in the data dir.')
    with open(path, 'rb') as f:
        reader = DictReader(f)
        for row in reader:
            try:
                interest = Interest.objects.get(name=row['name'])
                if not row['canonical'] and interest.canonical:
                    print "remove", interest
                    set_canonical(interest, None)
                else:
                    canonical = Interest.objects.get(name=row['canonical'])
                    if interest.canonical != canonical:
                        print "set", interest, canonical
                        set_canonical(interest, canonical)
            except (Interest.DoesNotExist, Interest.MultipleObjectsReturned) as e:
                print "skip", row['name'], row['canonical'], e
                # TODO
                continue


if __name__ == '__main__':
    import django
    django.setup()
    base_dir = os.path.dirname(__file__)
    path = os.path.join(
        base_dir, '..', '..', 'data', 'nomenklatura', 'interests.csv')
    go(path)
