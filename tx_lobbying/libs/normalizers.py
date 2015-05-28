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
            'FREEWAY': 'FWY',
            'FRWY': 'FWY',
            'LANE': 'LN',
            'PARKWAY': 'PKWY',
            'PLACE': 'PL',
            'ROAD': 'RD',
            'STREET': 'ST',
        }.get(x, x),
        'OccupancyType': lambda x: {
            'FLOOR': 'FL',
            'ST': 'STE',
            'SUITE': 'STE',
            'SUTIE': 'STE',
        }.get(x, x),
        'StreetNamePreDirectional': lambda x: {
            'EAST': 'E',
            'NORTH': 'N',
            'NORTHWEST': 'NW',
            'SOUTH': 'S',
            'SOUTHWEST': 'SW',
            'WEST': 'W',
        }.get(x, x),
        # XXX
        'USPSBoxType': lambda x: {
            'P O BOX': 'PO Box',
            'P O DRAWER': 'PO Drawer',
            'PO BOX': 'PO Box',
            'PO Drawer': 'PO Drawer',
            'POBOX': 'PO Box',
            'POST OFFICE BOX': 'PO Box',
        }.get(x, x),
    }
    value = value.replace('.', '')
    if label in formatters:
        return formatters[label](value.upper())
    return value


def clean_street(address1, address2='', zipcode=None):
    """
    Normalize street address.
    """
    # Matchers that rely on knowing address lines
    #############################################
    # Strip "care of" lines
    if re.match(r'c/o ', address1, re.IGNORECASE):
        address1 = ''

    # concatenate line 1 and line 2
    address = '{} {}'.format(address1, address2).strip()

    if not address:
        return address, None

    try:
        # Add arbitrary city/state/zip to get `usaddress` to parse the address
        # as just the street address and not a full address
        address_to_parse = '{}, Austin, TX {}'.format(address, zipcode) if zipcode else address
        addr_components, type_ = usaddress.tag(address_to_parse)
    except usaddress.RepeatedLabelError:
        logger.warn('Unparseable address: {}'.format(address_to_parse))
        return address, None
    if zipcode:
        try:
            addr_components.pop('PlaceName', None)
            addr_components.pop('StateName', None)
            guessed_zip = addr_components.pop('ZipCode')
            assert guessed_zip == zipcode
        except KeyError:
            logger.warn('Expected a zipcode {} but found none'.format('zipcode'))
        except AssertionError:
            logger.warn('Guessed the wrong zipcode {} != {}'
                        .format(guessed_zip, zipcode))
    if type_ not in ('Street Address', 'PO Box'):
        logger.warn('{} address: {}'.format(type_, address), extra=addr_components)
    normalized = ' '.join(
        [component_format(label, value) for label, value in addr_components.items()])
    return normalized, addr_components


def normalize_street(address1, address2='', zipcode=None):
    return clean_street(address1, address2, zipcode)[0]
