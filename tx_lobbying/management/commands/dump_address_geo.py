from django.core.management.base import BaseCommand


from .dump_lobbying_interests import UnicodeWriter


class Command(BaseCommand):
    def handle(self, *args, **options):
        from tx_lobbying.models import Address
        from sys import stdout

        fields = (
            'address1',
            'address2',
            'city',
            'state',
            'zipcode',
            'coordinate',
            'coordinate_quality',
        )
        writer = UnicodeWriter(stdout)
        writer.writerow(fields)  # header
        for address in Address.objects.filter(coordinate__isnull=False):
            writer.writerow([unicode(getattr(address, x)) for x in fields])
