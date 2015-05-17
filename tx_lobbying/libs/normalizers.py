from __future__ import unicode_literals

import logging
import re

import usaddress


logger = logging.getLogger(__name__)


# A zip+4 or zip+4 with a missing dash
zip_4 = re.compile(r'^\d{5}\-?(\d{4})?$')


def clean_zipcode(input):
    if zip_4.match(input):
        # malformed zip+4
        logger.debug('cleaned zip code: {}'.format(input))
        return input[0:5]
    return input


def component_format(label, value):
    formatters = {
        'StreetNamePostType': lambda x: {
            'AVENUE': 'AVE',
            'BOULEVARD': 'BLVD',
            'DRIVE': 'DR',
            'STREET': 'ST',
        }.get(x, x),
        'OccupancyType': lambda x: {
            'FLOOR': 'FL',
            'ST': 'STE',
            'SUITE': 'STE',
        }.get(x, x),
        'StreetNamePreDirectional': lambda x: {
            'EAST': 'E',
            'NORTH': 'NW',
            'SOUTH': 'S',
            'WEST': 'W',
        }.get(x, x),
        # 'USPSBoxType': lambda x: {
        #     'P O BOX': 'PO Box',
        #     'PO BOX': 'PO Box',
        # }.get(x, x),
    }
    value = value.replace('.', '')
    if label in formatters:
        return formatters[label](value.upper())
    return value


def clean_street(address1, address2=''):
    """
    Clean street address.
    """
    # matchers that rely on knowing address lines
    # Strip "care of" lines
    if re.match(r'c/o ', address1, re.IGNORECASE):
        return address2

    # concatenate line 1 and line 2
    address = '{} {}'.format(address1, address2).strip()

    if not address:
        return address

    try:
        addr, type_ = usaddress.tag(address)
    except usaddress.RepeatedLabelError as e:
        logger.warn(e)
        return address
    if type_ == 'Street Address':
        return ' '.join(
            [component_format(label, value) for label, value in addr.items()])
    elif type_ == 'PO Box':
        return ' '.join(
            [component_format(label, value) for label, value in addr.items()])
    logger.warn('Ambiguous address: {}'.format(address), extra=addr)
    return address
