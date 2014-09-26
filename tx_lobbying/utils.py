import logging
import os

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count
import requests

from .models import Address, Interest, Lobbyist


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


def update_addresses():
    """Collect addresses into canonical."""
    qs = (
        Address.objects
        .filter(coordinate_quality__in=('00', '01', '02', '03'))
        .order_by('coordinate').values('coordinate')
        .annotate(count=Count('pk'))
        .filter(count__gt=1)
    )
    for datum in qs:
        same = list(Address.objects.filter(coordinate=datum['coordinate'])
            # Assume the latest is the most up to date
            .order_by('-pk'))
        canon = same[0]
        print(canon)
        # ugh, must be a better way of doing this
        if canon.canonical:
            canon.canonical = None
            canon.save()
        for address in same[1:]:
            address.canonical = canon
            address.save()


class GeocodeException(Exception):
    pass


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
    if not address.city and not address.zipcode:
        raise GeocodeException("Can't look up without a city or zip")
    api_key = os.environ.get('TAMU_API_KEY')
    if not api_key:
        raise ImproperlyConfigured(
            "Can't look up without 'TAMU_API_KEY' environment variable")
    url = (
        'http://geoservices.tamu.edu/Services/Geocode/WebService/'
        'GeocoderWebServiceHttpNonParsed_V04_01.aspx'
    )
    params = {
        'apiKey': api_key,
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
        raise GeocodeException('Got a non-200 response: {}'
            .format(response.status_code))
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
