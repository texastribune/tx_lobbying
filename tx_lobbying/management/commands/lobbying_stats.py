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
                year_min = interest.years_available.earliest('year').year
                year_max = interest.years_available.latest('year').year
                for year in range(year_min, year_max + 1):
                    interest.make_stats_for_year(year)
                print u'{}/{} {}'.format(i, count, interest)
        except KeyboardInterrupt:
            exit(1)
