from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from tx_lobbying.utils import (update_lobbyists_stats,
            update_interests_stats)

        try:
            update_lobbyists_stats()
            update_interests_stats()
        except KeyboardInterrupt:
            exit(1)
