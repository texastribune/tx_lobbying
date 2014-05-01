"""
Scraper for Lobbyist Registration Forms.

The Excel formatted files can be obtained here:
http://www.ethics.state.tx.us/dfs/loblists.htm

Open and re-save as CSV.

"""
import json
import logging
import os
import sys

# don't use relative imports so this can also be run from the command line
from tx_lobbying.models import (Interest, Lobbyist, RegistrationReport,
    LobbyistYear, Compensation)
from tx_lobbying.scrapers.utils import (DictReader, convert_date_format_YMD)


logger = logging.getLogger(__name__)


def update_or_create_interest(row):
    """
    Update or create an `Interest`.

    Uses the name and state for uniquess. So we assume that AT&T Texas and AT&T
    DC are two separate interests, but AT&T Texas and AT & T Texas are the same.
    """
    # TODO get other info from the csv
    defaults = dict(
        address1=row['EC_ADR1'],
        address2=row['EC_ADR2'],
        city=row['EC_CITY'],
        state=row['EC_STCD'],
        zipcode=row['EC_ZIP4'],
    )
    interest, created = Interest.objects.update_or_create(
        name=row['CONCERNAME'],
        defaults=defaults,
    )
    return interest, created


def scrape(path, logger=logger):
    logger.info("Processing %s" % path)
    with open(path, 'rb') as f:
        reader = DictReader(f)
        for row in reader:
            report_date = convert_date_format_YMD(row['RPT_DATE'])
            year = row['YEAR_APPL']

            # interest/concern/client
            interest, created = update_or_create_interest(row)

            # lobbyist
            # very basic `Lobbyist` info here, most of it actually comes
            # from the coversheets.
            default_data = dict(
                name=row['LOBBYNAME'],
                sort_name=row['SORTNAME'],  # not LOB_SORT like in coversheets
                updated_at=report_date,
            )
            lobbyist, created = Lobbyist.objects.update_or_create(
                filer_id=row['FILER_ID'],
                defaults=default_data)
            if created:
                logger.info("LOBBYIST: %s" % lobbyist)

            # lobbyist/interest M2M
            lyear, created = LobbyistYear.objects.update_or_create(
                lobbyist=lobbyist,
                year=year)

            # compensation
            default_data = dict(
                amount_high=int(round(float(row['NHIGH'] or "0"))),  # I hate myself
                amount_low=int(round(float(row['NLOW'] or "0"))),
                raw=json.dumps(row),
                updated_at=report_date,
            )
            # WISHLIST move this amount_guess logic into the model
            default_data['amount_guess'] = (default_data['amount_high'] +
                default_data['amount_low']) / 2
            Compensation.objects.update_or_create(
                year=lyear,
                interest=interest,
                defaults=default_data)

            # registration report
            default_data = dict(
                raw=json.dumps(row),
                report_date=report_date,
                year=year,
            )
            report, created = RegistrationReport.objects.update_or_create(
                lobbyist=lobbyist,
                report_id=row['REPNO'],
                defaults=default_data)
            if created:
                logger.info("REPORT: %s" % report)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("hey, I need a file:\n  %s <input>" % sys.argv[0])
    input_csv_path = sys.argv[1]
    if not os.path.isfile(input_csv_path):
        exit("hey, %s is not a file" % input_csv_path)
    scrape(input_csv_path)
