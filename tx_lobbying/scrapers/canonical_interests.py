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


def process_row(row):
    to_update = []
    try:
        interest = Interest.objects.get(name=row['name'])
        # assert row['id']
        if interest.nomenklatura_id != row['id']:
            interest.nomenklatura_id = row['id']
            interest.save()
        if row['canonical']:
            canonical = Interest.objects.get(name=row['canonical'])
            if interest.canonical != canonical:
                print "set", interest, canonical
                set_canonical(interest, canonical)
                to_update.extend((interest, canonical))
        elif interest.canonical:
            print "remove", interest
            set_canonical(interest, None)
            to_update.append(interest)
        return to_update
    except Interest.MultipleObjectsReturned as e:
        print "skip", row['name'], row['canonical'], e
        # TODO
        pass
    except Interest.DoesNotExist:
        pass


def go(path):
    if not os.path.isfile(path):
        exit('Make sure you ran `make nomenklatura` in the data dir.')
    interests_to_update = set()
    with open(path, 'rb') as f:
        reader = DictReader(f)
        for row in reader:
            interests_touched = process_row(row)
            for interest in interests_touched:
                interests_to_update.add(interest)
    for interest in interests_to_update:
        print 'update', interest
        interest.make_stats()


if __name__ == '__main__':
    import django
    django.setup()
    base_dir = os.path.dirname(__file__)
    path = os.path.join(
        base_dir, '..', '..', 'data', 'nomenklatura', 'interests.csv')
    go(path)
