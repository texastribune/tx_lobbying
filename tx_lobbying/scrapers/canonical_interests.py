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
    try:
        interest = Interest.objects.get(name=row['name'])
        # assert row['id']
        if interest.nomenklatura_id != row['id']:
            interest.nomenklatura_id = row['id']
            # ok to incur this extra save because it only happens the first time
            interest.save()
        if row['canonical']:
            canonical = Interest.objects.get(name=row['canonical'])
            if interest.canonical != canonical:
                print('set {} canonical: {}'.format(interest, canonical))
                set_canonical(interest, canonical)
                return True
        elif interest.canonical:
            print "remove", interest
            set_canonical(interest, None)
            return True
    except Interest.MultipleObjectsReturned as e:
        print "skip", row['name'], row['canonical'], e
        # TODO
        pass
    except Interest.DoesNotExist:
        # don't care if source has extra interests
        pass


def go(path, max_attempts=5):
    if not os.path.isfile(path):
        exit('Make sure you ran `make nomenklatura` in the data dir.')
    with open(path, 'rb') as f:
        reader = DictReader(f)
        update_attempts = 0
        restarts = 0
        for row in reader:
            is_updated = process_row(row)
            if is_updated:
                if update_attempts:
                    update_attempts = 0  # reset counter
                    restarts += 1  # log how many times we've reset the counter
            else:
                update_attempts += 1
                if update_attempts >= max_attempts:
                    print('skipping the rest after trying {} and {} resets'
                        .format(update_attempts, restarts))
                    # we're just running through old entries at this point
                    # since the datafile is in reverse chronological order
                    break
    # these `Interest`s need updated stats
    for interest in Interest.objects.filter(
            canonical__isnull=True, stats__isnull=True):
        print 'update', interest
        interest.make_stats()


if __name__ == '__main__':
    import django
    django.setup()
    base_dir = os.path.dirname(__file__)
    path = os.path.join(
        base_dir, '..', '..', 'data', 'nomenklatura', 'interests.csv')
    go(path)
