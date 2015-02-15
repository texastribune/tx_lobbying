from optparse import make_option
import os

from django.core.management.base import BaseCommand
import requests


class Command(BaseCommand):
    help = 'Geocode some addresses, waits 10 seconds'
    option_list = BaseCommand.option_list + (
        make_option('--random', action='store_true', dest='random',
            help='Pick addresses at random'),
    )

    def get_remaining_credits(self):
        # if you run out of credits, go to
        # https://geoservices.tamu.edu/UserServices/Payments/
        api_key = os.environ.get('TAMU_API_KEY')
        assert api_key
        url = ('https://geoservices.tamu.edu/UserServices/Payments/Balance/'
            'AccountBalanceWebServiceHttp.aspx?'
            'version=1.0&apikey={}&format=csv'.format(api_key))
        response = requests.get(url)
        assert response.ok
        key, credits = response.text.split(',')
        assert key == api_key
        return int(credits)

    def handle(self, *args, **options):
        from tx_lobbying.utils import geocode_address
        from tx_lobbying.models import Address
        from time import sleep

        credit = self.get_remaining_credits()
        self.stdout.write('# of api credits remaining: {}'.format(credit))

        # pull in the same order so it's repeatable
        queryset = (
            Address.objects
            .filter(coordinate__isnull=True)
            .exclude(zipcode='')
        )
        self.stdout.write('# of addresses to geocode: {}'.format(queryset.count()))

        if options['random']:
            # not very efficient, but is terse
            queryset = queryset.order_by('?')

        try:
            for address in queryset[:credit]:
                self.stdout.write('*' * 40)
                self.stdout.write(address.get_display_name(sep=', '))
                self.stdout.write(unicode(geocode_address(address)))
                sleep(10)
        except KeyboardInterrupt:
            exit('bye')
