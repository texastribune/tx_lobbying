"""
Scraper for Lobbyist Registration Forms.

The Excel formatted files can be obtained here:
http://www.ethics.state.tx.us/dfs/loblists.htm

Open and re-save as CSV.

"""
from csv import DictReader
import json
import logging
import os
import sys

# don't use relative imports so this can also be run from the command line
from tx_lobbying.models import (Interest, Lobbyist, RegistrationReport,
    ClientList, Compensation)


logger = logging.getLogger(__name__)


def convert_date_format(str):
    """Convert 12/25/2009 to 2009-12-25."""
    # TODO convert to Date so we can do comparisons
    month, day, year = str.split('/')
    return u"-".join([year, month, day])


def scrape(path):
    logger.info("Processing %s" % path)
    with open(path, 'r') as f:
        reader = DictReader(f)
        for row in reader:
            report_date = convert_date_format(row['RPT_DATE'])
            year = row['YEAR_APPL']

            # interest/concern/client
            interest, created = Interest.objects.get_or_create(
                name=row['CONCERNAME'],
                state=row['EC_STCD'])

            # lobbyist
            default_data = dict(
                sort_name=row['SORTNAME'],
                updated_at=report_date,
            )
            lobbyist, created = Lobbyist.objects.get_or_create(
                filer_id=row['FILER_ID'],
                defaults=default_data)
            if not created:
                # need to update name?
                pass
            if created:
                logger.debug(lobbyist)

            # lobbyist/interest M2M
            clientlist, created = ClientList.objects.get_or_create(
                lobbyist=lobbyist,
                year=year)
            default_data = dict(
                amount_high=int(round(float(row['NHIGH']))),  # I hate myself
                amount_low=int(round(float(row['NLOW']))),
                raw=json.dumps(row),
                updated_at=report_date,
            )
            default_data['amount_guess'] = (default_data['amount_high'] +
                default_data['amount_low']) / 2
            Compensation.objects.get_or_create(
                clientlist=clientlist,
                interest=interest,
                defaults=default_data)

            # report
            report_id = row['REPNO']
            default_data = dict(
                raw=json.dumps(row),
                report_date=report_date,
                year=year,
            )
            report, created = RegistrationReport.objects.get_or_create(
                filer=lobbyist,
                report_id=report_id,
                defaults=default_data)
            if created:
                logger.debug(report)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("hey, I need a file:\n  %s <input>" % sys.argv[0])
    input_csv_path = sys.argv[1]
    if not os.path.isfile(input_csv_path):
        exit("hey, %s is not a file" % input_csv_path)
    scrape(input_csv_path)
