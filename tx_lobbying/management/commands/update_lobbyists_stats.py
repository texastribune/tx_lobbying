from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **options):
        from ...utils import update_lobbyists_stats
        try:
            update_lobbyists_stats()
        except KeyboardInterrupt:
            exit(1)
