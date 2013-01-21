import logging

from .models import Lobbyist


logger = logging.getLogger(__name__)


def update_lobbyists_stats(starting=None):
    """Update `Lobbyist` expense stats."""
    qs = Lobbyist.objects.all()
    # qs = qs.filter(updated_at__gte=starting)
    total = qs.count()
    for i, l in enumerate(qs, 1):
        logger.info("{:>4} / {} - {}".format(i, total, l))
        l.make_stats()
