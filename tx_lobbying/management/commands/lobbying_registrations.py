from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        import os

        from ...scrapers.registration import scrape

        if len(args) < 1 or not os.path.isfile(args[0]):
            raise CommandError('Need a file')
        try:
            scrape(args[0])
        except KeyboardInterrupt:
            exit(1)
