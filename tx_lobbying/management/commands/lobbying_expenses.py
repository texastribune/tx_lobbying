from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('directory')

    def handle(self, **options):
        import logging
        import os

        # from project_runpy import ColorizingStreamHandler

        from ...scrapers.expenses import main

        if not os.path.isdir(options['directory']):
            raise CommandError('Need a directory')

        verbosity = int(options['verbosity'])
        if verbosity == 0:
            logging.getLogger('tx_lobbying.scrapers.expenses').setLevel(logging.ERROR)
        elif verbosity == 1:  # default
            logging.getLogger('tx_lobbying.scrapers.expenses').setLevel(logging.WARN)
        elif verbosity > 1:
            logging.getLogger('tx_lobbying.scrapers.expenses').setLevel(logging.DEBUG)
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)

        try:
            main(options['directory'])
        except KeyboardInterrupt:
            exit(1)
