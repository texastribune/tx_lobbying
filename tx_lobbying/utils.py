import logging
import os

import requests

from .models import Interest, Lobbyist


logger = logging.getLogger(__name__)


def update_lobbyists_stats(starting=None):
    """Update `Lobbyist` expense stats."""
    qs = Lobbyist.objects.all()
    # qs = qs.filter(updated_at__gte=starting)
    count = qs.count()
    for i, l in enumerate(qs, 1):
        logger.info("{:>4} / {} - {}".format(i, count, l))
        l.make_stats()


def update_interests_stats():
    qs = Interest.objects.filter(canonical__isnull=True)
    count = qs.count()
    for i, interest in enumerate(qs, 1):
        logger.info(u'{:>4} / {} - {}'.format(i, count, interest))
        interest.make_stats()


def geocode_address(address, force=False):
    """
    Geocode an `Address`.

    Examples:
    http://geoservices.tamu.edu/Services/Geocode/WebService/v04_01/Simple/Rest/
    """
    from django.contrib.gis.geos import Point
    if address.coordinate and not force:
        # address already has a location
        return
    url = (
        'http://geoservices.tamu.edu/Services/Geocode/WebService/'
        'GeocoderWebServiceHttpNonParsed_V04_01.aspx'
    )
    params = {
        'apiKey': os.environ.get('TAMU_API_KEY'),
        'version': '4.01',
        'streetAddress': address.address1,
        'city': address.city,
        'state': address.state,
        'zip': address.zipcode,
    }
    headers = {
        'user-agent': 'default/lobbying v0.0'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        # TODO raise an exception
        return
    fields = [
        'TransactionId',
        'Version',
        'QueryStatusCodeValue',
        'Latitude',
        'Longitude',
        'NAACCRGISCoordinateQualityCode',
        'NAACCRGISCoordinateQualityName',
        'MatchScore',
        'MatchType',
        'FeatureMatchingResultType',
        'FeatureMatchingResultCount',
        'FeatureMatchingGeographyType',
        'RegionSize',
        'RegionSizeUnits',
        'MatchedLocationType',
        'TimeTaken',
    ]
    data = dict(zip(fields, response.text.split(',')))
    address.coordinate = Point(
        x=float(data['Longitude']),
        y=float(data['Latitude']),
    )
    address.coordinate_quality = data['NAACCRGISCoordinateQualityCode']
    address.save()
    return data
