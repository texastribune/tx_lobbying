import logging
import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        from ...scrapers.registration import scrape

        if len(args) < 1 or not os.path.isfile(args[0]):
            raise CommandError('Need a file')

        verbosity = int(options['verbosity'])
        if verbosity == 0:
            logging.getLogger('tx_lobbying.scrapers.registration').setLevel(logging.WARN)
        elif verbosity == 1:  # default
            logging.getLogger('tx_lobbying.scrapers.registration').setLevel(logging.INFO)
        elif verbosity > 1:
            logging.getLogger('tx_lobbying.scrapers.registration').setLevel(logging.DEBUG)
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)

        try:
            scrape(args[0])
        except KeyboardInterrupt:
            exit(1)
