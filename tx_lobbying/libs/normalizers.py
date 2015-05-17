"""
Take address objects and clean each individual fields.

Other examples that all take full addresses:

* http://pyparsing.wikispaces.com/file/view/streetAddressParser.py
* https://github.com/pnpnpn/street-address
* https://github.com/SwoopSearch/pyaddress
"""
from __future__ import unicode_literals

import logging
import re

logger = logging.getLogger(__name__)


def clean_zipcode(input):
    if len(input) == 9:
        # malformed zip+4
        logger.debug('cleaned zip code: {}'.format(input))
        return '{}-{}'.format(input[0:5], input[5:])
    return input


def clean_street(input):
    # TODO
    return input
