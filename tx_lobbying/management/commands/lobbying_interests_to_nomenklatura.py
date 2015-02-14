from django.core.management.base import BaseCommand

from .dump_lobbying_interests import UnicodeWriter


class Command(BaseCommand):
    help = ('Export interests for opennames.org. When importing, set state '
        'to "Acronym" and address to "Biography" and uncheck '
        '"Consider imported entities reviewed"')

    def handle(self, *args, **options):
        from tx_lobbying.models import Interest
        from sys import stdout

        writer = UnicodeWriter(stdout)
        writer.writerow(('name', 'state', 'address'))
        for interest in Interest.objects.filter(nomenklatura_id=None).select_related('address'):
            row = (
                interest.name,
                unicode(interest.address.state),
                unicode(interest.address),
            )
            writer.writerow(row)
