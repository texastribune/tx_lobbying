"""

I'm too lazy to do unicode csv reading the "proper" way, so you're going to see
a lot of stupid .decode('latin_1') calls.

"""
from calendar import timegm
from csv import DictReader
import datetime
import logging
import os
import time
import urllib

# don't use relative imports so this can also be run from the command line
from tx_lobbying.models import (Lobbyist, Coversheet)
from tx_lobbying.scrapers.utils import convert_date_format, setfield


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


def covers(path):
    logger.info("Processing %s" % path)
    with open(path, 'r') as f:
        reader = DictReader(f)
        for row in reader:
            try:
                report_date = row['FILED_DATE'] or row['RPT_DATE']
                report_date = convert_date_format(report_date)
            except:
                logger.warn('Row missing data: %s' % row)
                raise
                continue

            default_data = dict(
                sort_name=row['LOB_SORT'],
                updated_at=report_date)
            lobbyist, dirty = Lobbyist.objects.get_or_create(
                filer_id=row['FILER_ID'],
                defaults=default_data
                )
            if report_date > lobbyist.updated_at:
                setfield(lobbyist, 'first_name', row['FILER_NAMF'].decode('latin_1'))
                setfield(lobbyist, 'last_name', row['FILER_NAML'].decode('latin_1'))
                setfield(lobbyist, 'title', row['FILER_NAMT'].decode('latin_1'))
                setfield(lobbyist, 'suffix', row['FILER_NAMS'].decode('latin_1'))
                setfield(lobbyist, 'nick_name', row['FILERSHORT'].decode('latin_1'))
                setfield(lobbyist, 'updated_at', report_date)
            if getattr(lobbyist, '_is_dirty', None):
                logger.debug("{} {} {}".format(lobbyist._is_dirty, report_date, lobbyist.updated_at))
                lobbyist.save()
                del lobbyist._is_dirty
                dirty = True
            if dirty:
                logger.info("LOBBYIST: %s" % lobbyist)

            default_data = dict(
                lobbyist=lobbyist,
                report_date=report_date,
                year=row['YEAR_APPL'],
            )
            cover, dirty = Coversheet.objects.get_or_create(
                report_id=row['REPNO'],
                defaults=default_data)
            if report_date > cover.report_date:
                setfield(cover, 'report_date', report_date)
            if getattr(cover, '_is_dirty', None):
                logger.debug(lobbyist._is_dirty)
                cover.save()
                del cover._is_dirty
                dirty = True
            if dirty:
                logger.info("COVER: %s" % cover)

if __name__ == "__main__":
    files = download_zip(url=TEC_URL, extract_to=DATA_DIR)

    cover_csv = os.path.join(DATA_DIR, "LaCVR.csv")
    if cover_csv in files:
        covers(cover_csv)
