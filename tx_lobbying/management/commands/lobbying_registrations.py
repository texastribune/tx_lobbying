from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        import logging
        import os

        # from project_runpy import ColorizingStreamHandler

        from ...scrapers.registration import scrape

        if len(args) < 1 or not os.path.isfile(args[0]):
            raise CommandError('Need a file')

        logging_levels = [
            logging.CRITICAL,
            logging.WARNING,  # default
            logging.INFO,
            logging.DEBUG
        ]
        logging_level = logging_levels[int(options['verbosity'])]
        logger = logging.getLogger(__name__)
        logger.setLevel(logging_level)
        # if options['no_color']:
        #     logger.addHandler(logging.StreamHandler())
        # else:
        #     logger.addHandler(ColorizingStreamHandler())

        try:
            scrape(args[0], logger=logger)
        except KeyboardInterrupt:
            exit(1)
