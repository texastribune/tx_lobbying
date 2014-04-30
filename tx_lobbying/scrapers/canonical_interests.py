"""
TODO change print to logger
"""
import logging
import os

from tx_lobbying.models import Interest
from tx_lobbying.scrapers.utils import DictReader


logger = logging.getLogger(__name__)


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
                    interest.stats.all().delete()
                    interest.canonical.stats.all().delete()
                    interest.canonical = None
                    interest.save()
                else:
                    canonical = Interest.objects.get(name=row['canonical'])
                    if interest.canonical != canonical:
                        print "set", interest, canonical
                        interest.canonical = canonical
                        interest.save(update_fields=('canonical', ))
                        interest.stats.all().delete()
                        canonical.stats.all().delete()
            except (Interest.DoesNotExist, Interest.MultipleObjectsReturned):
                print "skip", interest
                # TODO
                continue


if __name__ == '__main__':
    import django
    django.setup()
    base_dir = os.path.dirname(__file__)
    path = os.path.join(
        base_dir, '..', '..', 'data', 'nomenklatura', 'interests.csv')
    go(path)
