import datetime
import logging
import os
import urllib
from calendar import timegm
import time

from tx_lobbying.models import (Lobbyist, LobbyistYear)


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


if __name__ == "__main__":
    files = download_zip(url=TEC_URL, extract_to=DATA_DIR)
    print files
