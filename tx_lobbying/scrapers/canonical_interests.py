"""
Make sure you ran `make nomenklatura/interests.csv` in the data dir.
"""
import logging
import os

from tx_lobbying.models import Interest
from tx_lobbying.scrapers.utils import DictReader


logger = logging.getLogger(__name__)


def go():
    with open(os.path.join('..', '..', 'data', 'nomenklatura', 'interests.csv'), 'rb') as f:
        reader = DictReader(f)
        for row in reader:
            if not row['canonical']:
                continue
            try:
                interest = Interest.objects.get(name=row['name'])
                canonical = Interest.objects.get(name=row['canonical'])
                if interest.canonical != canonical:
                    print "set", interest, canonical
                    interest.canonical = canonical
                    interest.save(update_fields=('canonical', ))
            except (Interest.DoesNotExist, Interest.MultipleObjectsReturned):
                print "skip", interest
                # TODO
                continue


if __name__ == '__main__':
    import django
    django.setup()
    go()
