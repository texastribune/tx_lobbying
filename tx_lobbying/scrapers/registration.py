"""
Scraper for Lobbyist Registration Forms.

The Excel formatted files can be obtained here:
http://www.ethics.state.tx.us/dfs/loblists.htm

Use csvkit's `in2csv` or open and re-save as CSV.
"""
from collections import namedtuple
import json
import logging
import os
import sys

from django.utils.text import slugify

# don't use relative imports so this can also be run from the command line
from tx_lobbying.libs.address_normalizer import clean_zipcode
from tx_lobbying.models import (
    Address,
    Interest, Lobbyist, RegistrationReport,
    LobbyistAnnum, Compensation)
from tx_lobbying.scrapers.utils import (DictReader, convert_date_format_YMD)


logger = logging.getLogger(__name__)
ProcessedRow = namedtuple('ProcessedRow',
    ['address', 'lobbyist', 'report', 'compensation'])


def get_or_create_interest(row):
    """
    Update or create an `Interest`.

    Uses the name and state for uniquess. So we assume that AT&T Texas and AT&T
    DC are two separate interests, but AT&T Texas and AT & T Texas are the same.
    """
    address, __ = Address.objects.get_or_create(
        address1=row['EC_ADR1'],
        address2=row['EC_ADR2'],
        city=row['EC_CITY'],
        state=row['EC_STCD'],
        zipcode=clean_zipcode(row['EC_ZIP4']),
    )
    # TODO get other info from the csv
    defaults = dict(
        address=address,
        slug=slugify(unicode(row['CONCERNAME'])),
    )
    interest, created = Interest.objects.get_or_create(
        name=row['CONCERNAME'],
        defaults=defaults,
    )
    return interest, address, created


def process_row(row, prev_pass=None):
    """
    Process a row of the CSV.

    If you pass in the previous output, some optimization will take place to
    process things faster. There is a lot of duplication in the raw data that
    can get skipped.

    You'd think you could just see if the report id changes between rows to see
    if the lobbyist changes, but it turns out that isn't always true. So do a
    manual check of every feature to squeeze out reusing the previous pass as
    much as possible.

    Compensation objects get created outside in a bulk_create for performance.
    """
    report_date = convert_date_format_YMD(row['RPT_DATE'])
    year = row['YEAR_APPL']

    data = dict(
        address1=row['ADDRESS1'],
        address2=row['ADDRESS2'],
        city=row['CITY'],
        state=row['STATE'],
        zipcode=row['ZIPCODE'],
    )
    # HAHAHAHAHAHA
    if (prev_pass and prev_pass.address.address1 == data['address1']
            and prev_pass.address.address2 == data['address2']
            and prev_pass.address.city == data['city']
            and prev_pass.address.state == data['state']
            and prev_pass.address.zipcode == data['zipcode']):
        reg_address = prev_pass.address
    else:
        reg_address, __ = Address.objects.get_or_create(**data)

    # Very basic `Lobbyist` info here, most of it actually comes from the
    # coversheets.
    if prev_pass and prev_pass.lobbyist.filer_id == int(row['FILER_ID']):
        lobbyist = prev_pass.lobbyist
    else:
        default_data = dict(
            name=row['LOBBYNAME'],
            sort_name=row['SORTNAME'],  # not LOB_SORT like in coversheets
            updated_at=report_date,
            address=reg_address,
            slug=slugify(unicode(row['LOBBYNAME'])),
        )
        lobbyist, created = Lobbyist.objects.update_or_create(
            filer_id=row['FILER_ID'],
            defaults=default_data)
        if created:
            logger.info("LOBBYIST: %s" % lobbyist)

    if row['CONCERNAME']:
        # interest/concern/client
        interest, interest_address, __ = get_or_create_interest(row)
    else:
        interest_address = None
        interest = None

    # registration report
    if prev_pass and prev_pass.report.report_id == int(row['REPNO']):
        report = prev_pass.report
    else:
        default_data = dict(
            raw=json.dumps(row),
            report_date=report_date,
            year=year,
            address=reg_address,
        )
        report, created = RegistrationReport.objects.update_or_create(
            lobbyist=lobbyist,
            report_id=row['REPNO'],
            defaults=default_data)
        if created:
            logger.info("REPORT: %s" % report)

    if interest:
        # lobbyist M2M to `Interest` through `Compensation`
        annum, __ = LobbyistAnnum.objects.update_or_create(
            lobbyist=lobbyist,
            year=year)
        # compensation
        data = dict(
            amount_high=int(round(float(row['NHIGH'] or "0"))),  # I hate myself
            amount_low=int(round(float(row['NLOW'] or "0"))),
            compensation_type=row['TYPECOPM'],
            address=interest_address,
            raw=json.dumps(row),
            updated_at=report_date,
            report=report,
            client_num=row['CLIENT_NUM'],
        )
        if row['STARTDT']:
            data['start_date'] = row['STARTDT']
        if row['TERMDATE']:
            data['end_date'] = row['TERMDATE']
        # WISHLIST move this amount_guess logic into the model
        data['amount_guess'] = (data['amount_high'] +
            data['amount_low']) / 2
        compensation = Compensation(
            annum=annum,
            interest=interest,
            **data)
    else:
        compensation = None
    return ProcessedRow(reg_address, lobbyist, report, compensation)


def scrape(path, logger=logger):
    logger.info("Processing %s" % path)
    with open(path, 'rb') as f:
        reader = DictReader(f)
        prev_pass = None
        first = True
        new_compensations = []
        for row in reader:
            if first:
                # wipe all `Compensation` objects for the year to avoid double
                # counting corrected compensations
                year = row['YEAR_APPL']
                Compensation.objects.filter(annum__year=year).delete()
                first = False
            prev_pass = process_row(row, prev_pass=prev_pass)
            if prev_pass.compensation:
                new_compensations.append(prev_pass.compensation)
        logger.info('{} new compensations'.format(len(new_compensations)))
        Compensation.objects.bulk_create(new_compensations)


def generate_test_row(path, **kwargs):
    """Helper to replace `scrape` to print out a sample for testing."""
    import random
    from pprint import pprint

    with open(path, 'rb') as f:
        reader = DictReader(f)
        for row in reader:
            if random.randint(0, 99) < 1:  # adjust this to go deeper
                pprint(row)
                break
# scrape = generate_test_row


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("hey, I need a file:\n  %s <input>" % sys.argv[0])
    input_csv_path = sys.argv[1]
    if not os.path.isfile(input_csv_path):
        exit("hey, %s is not a file" % input_csv_path)
    scrape(input_csv_path)
