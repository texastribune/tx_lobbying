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

        logging_levels = [
            logging.CRITICAL,
            logging.WARNING,  # default
            logging.INFO,
            logging.DEBUG
        ]
        logging_level = logging_levels[int(options['verbosity'])]

        try:
            main(options['directory'], logging_level=logging_level)
        except KeyboardInterrupt:
            exit(1)
