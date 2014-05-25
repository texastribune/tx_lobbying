from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        from tx_lobbying.utils import geocode_address
        from tx_lobbying.models import Address
        from time import sleep

        # pull in the same order so it's repeatable
        # TODO add option to order by '?' so it fills in randomly
        queryset = (
            Address.objects
            .filter(coordinate__isnull=True)
            .exclude(zipcode='')
        )

        for address in queryset:
            print address
            print geocode_address(address)
            sleep(10)
