from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from ...models import Interest
        from ...utils import update_lobbyists_stats

        try:
            # lobbyist stats
            update_lobbyists_stats()

            # interest stats
            qs = Interest.objects.all()
            count = qs.count()
            for i, interest in enumerate(qs):
                interest.make_stats()
                print u'{}/{} {}'.format(i, count, interest)
        except KeyboardInterrupt:
            exit(1)
