from optparse import make_option

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Geocode some addresses, waits 10 seconds'
    option_list = BaseCommand.option_list + (
        make_option('--random', action='store_true', dest='random',
            help='Pick addresses at random'),
    )

    def handle(self, *args, **options):
        from tx_lobbying.utils import geocode_address
        from tx_lobbying.models import Address
        from time import sleep

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
            for address in queryset:
                self.stdout.write('*' * 40)
                self.stdout.write(address.get_display_name(sep=', '))
                self.stdout.write(unicode(geocode_address(address)))
                sleep(10)
        except KeyboardInterrupt:
            exit('bye')
