"""

I'm too lazy to do unicode csv reading the "proper" way, so you're going to see
a lot of stupid .decode('latin_1') calls.

"""
from __beyond__ import disable_django_db_logging
from calendar import timegm
import datetime
import json
import logging
import os
import time
import urllib

# don't use relative imports so this can also be run from the command line
from tx_lobbying.models import (Lobbyist, Coversheet)
from tx_lobbying.scrapers.utils import (DictReader, convert_date_format,
    get_name_data, setfield)


# CONFIGURATION
DATA_DIR = '.csv-cache'
TIME_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'
STALE_DAYS = 7  # expect errors from rounding and utc offset
TEC_URL = 'http://www.ethics.state.tx.us/tedd/TEC_LA_CSV.zip'


logger = logging.getLogger(__name__)


def download_zip(url, extract_to, force=False):
    """
    Return a list of files fresh from the TEC oven.

    Downloads to a temporary file and extracts it using your OS's unzip to
    `extract_to`. This only happens if the local copy of the data exists and
    isn't stale.

    """
    def get_remote_mtime():
        data = urllib.urlopen(url)
        date = data.info()['last-modified']
        logger.debug("remote modified: %s" % date)
        return timegm(time.strptime(date, TIME_FORMAT))

    def get_local_mtime():
        date = 0
        try:
            # BUG: utc offset gets applied wrong, but we don't care
            date = int(os.path.getmtime(os.path.join(
                extract_to, os.listdir(extract_to)[0])))
        except IndexError:
            pass
        logger.debug("local modified: %s" %
            datetime.datetime.fromtimestamp(date).strftime(TIME_FORMAT))
        return date

    if not os.path.exists(extract_to):
        os.mkdir(extract_to)

    local_mtime = get_local_mtime()
    staleness = abs(time.time() - local_mtime) / 86400
    logger.debug('Local Stale Check: ~%s days off' % staleness)
    if staleness > STALE_DAYS:
        remote_mtime = get_remote_mtime()
        staleness = abs(remote_mtime - local_mtime) / 86400
        logger.debug('Remote Stale Check: ~%s days off' % staleness)
    if force or staleness > STALE_DAYS:
        logger.info('Too stale: Pulling new files')
        filename, header = urllib.urlretrieve(url)
        os.system('unzip %s -d %s' % (filename, os.path.abspath(extract_to)))
    return [os.path.join(extract_to, f) for f in os.listdir(extract_to)
            if f[-3:] == 'csv']


def _covers_inner(row):
    report_date = row['FILED_DATE'] or row['RPT_DATE']
    report_date = convert_date_format(report_date)

    # Lobbyist
    default_data = dict(
        updated_at=report_date)
    default_data.update(get_name_data(row))
    lobbyist, dirty = Lobbyist.objects.get_or_create(
        filer_id=row['FILER_ID'],
        defaults=default_data, )
    if report_date > lobbyist.updated_at:
        for key, value in default_data.items():
            setfield(lobbyist, key, value)
    if getattr(lobbyist, '_is_dirty', None):
        logger.debug(lobbyist._is_dirty)
        lobbyist.save()
        del lobbyist._is_dirty
        dirty = True
    if dirty:
        logger.info("LOBBYIST: %s" % lobbyist)

    # Coversheet
    default_data = dict(
        lobbyist=lobbyist,
        raw=json.dumps(row),
        report_date=report_date,
        year=row['YEAR_APPL'],
        transportation=row['EXTYP_TRAN'] or "0.00",
        food=row['EXTYP_FOOD'] or "0.00",
        entertainment=row['EXTYP_GIFT'] or "0.00",
        gifts=row['EXTYP_GIFT'] or "0.00",
        awards=row['EXTYP_AWDS'] or "0.00",
        events=row['EXTYP_EVNT'] or "0.00",
        media=row['EXTYP_MEDA'] or "0.00",
        ben_senators=row['EXBEN_SEN'] or "0.00",
        ben_representatives=row['EXBEN_REP'] or "0.00",
        ben_other=row['EXBEN_OTH'] or "0.00",
        ben_legislative=row['EXBEN_LEG'] or "0.00",
        ben_executive=row['EXBEN_EXEC'] or "0.00",
        ben_family=row['EXBEN_FAM'] or "0.00",
        ben_events=row['EXBEN_EVNT'] or "0.00",
        ben_guests=row['EXBEN_GUES'] or "0.00",
    )
    total_spent = sum(float(y or 0) for x, y in row.items() if x.startswith("EXTYP"))
    total_benefited = sum(float(y or 0) for x, y in row.items() if x.startswith("EXBEN"))
    default_data['total_spent'] = total_spent
    default_data['total_benefited'] = total_benefited
    default_data['spent_guess'] = max(total_spent, total_benefited)

    cover, dirty = Coversheet.objects.get_or_create(
        report_id=row['REPNO'],
        defaults=default_data, )
    if report_date > cover.report_date:
        for key, value in default_data.items():
            setfield(cover, key, value)
    if getattr(cover, '_is_dirty', None):
        logger.debug(cover._is_dirty)
        cover.save()
        del cover._is_dirty
        dirty = True
    if dirty:
        logger.info("COVER: %s" % cover)


def covers(path):
    logger.info("Processing %s" % path)
    with open(path, 'r') as f:
        reader = DictReader(f, encoding="latin_1")
        for row in reader:
            try:
                _covers_inner(row)
            except ValueError:
                logger.warn('Row missing data: %s' % row)
                continue


if __name__ == "__main__":
    files = download_zip(url=TEC_URL, extract_to=DATA_DIR)

    cover_csv = os.path.join(DATA_DIR, "LaCVR.csv")
    if cover_csv in files:
        covers(cover_csv)
