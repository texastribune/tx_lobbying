from django.core.management.base import BaseCommand

from tx_lobbying.scrapers.utils import DictReader


class Command(BaseCommand):
    def handle(self, csv_path, *args, **options):
        from tx_lobbying.models import Address

        with open(csv_path, 'rb') as f:
            reader = DictReader(f)
            for row in reader:
                address, created = Address.objects.update_or_create(
                    address1=row['address1'],
                    address2=row['address2'],
                    city=row['city'],
                    state=row['state'],
                    zipcode=row['zipcode'],
                    defaults=dict(
                        coordinate=row['coordinate'],
                        coordinate_quality=row['coordinate_quality'],
                    )
                )
                print address, created
