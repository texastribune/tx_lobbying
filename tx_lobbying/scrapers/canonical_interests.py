#!/usr/bin/env python
"""
Usage:
  ./canonical_interests.py [options]

Options:
  --max-attempts=<n>  Maximum number of stale rows before quitting [default: 5]
  --input=<path>      Specify alternate CSV input


TODO change print to logger
TODO set max attempts via command line
"""
from __future__ import unicode_literals

import logging
import os

from docopt import docopt

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
    """
    Process a row of the nomenklatura csv.

    Returns a bool indicating if this did any work.
    """
    did_update = False
    try:
        interest = Interest.objects.get(name=row['name'])
        # assert row['id']
        if unicode(interest.nomenklatura_id) != row['id']:
            interest.nomenklatura_id = row['id']
            # ok to incur this extra save because it only happens the first time
            interest.save()
            print('linking {}'.format(interest.name))
            did_update = True
        if row['canonical']:
            canonical = Interest.objects.get(name=row['canonical'])
            if interest.canonical != canonical:
                print('SET {} ==> {}'.format(interest.name, canonical.name))
                set_canonical(interest, canonical)
                did_update = True
        elif interest.canonical:
            print('REMOVE {}'.format(interest))
            set_canonical(interest, None)
            did_update = True
    except Interest.MultipleObjectsReturned as e:
        print "skip", row['name'], row['canonical'], e
        # TODO
        pass
    except Interest.DoesNotExist:
        # don't care if source has extra interests
        print('extra: {}'.format(row['name']))
        pass
    return did_update


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
    options = docopt(__doc__)
    import django; django.setup()  # NOQA
    max_attempts = int(options['--max-attempts'])
    if options['--input']:
        path = options['--input']
    else:
        base_dir = os.path.dirname(__file__)
        path = os.path.join(
            base_dir, '..', '..', 'data', 'nomenklatura', 'interests_sorted.csv')
    go(path, max_attempts)
