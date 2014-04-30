import logging

from .models import Interest, Lobbyist


logger = logging.getLogger(__name__)


def update_lobbyists_stats(starting=None):
    """Update `Lobbyist` expense stats."""
    qs = Lobbyist.objects.all()
    # qs = qs.filter(updated_at__gte=starting)
    total = qs.count()
    for i, l in enumerate(qs, 1):
        logger.info("{:>4} / {} - {}".format(i, total, l))
        l.make_stats()


def update_interests_stats():
    qs = Interest.objects.all()
    count = qs.count()
    for i, interest in enumerate(qs):
        interest.make_stats()
        print u'{}/{} {}'.format(i, count, interest)
