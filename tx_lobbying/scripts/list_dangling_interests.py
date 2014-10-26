#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Export all Interests that haven't been evaluated.
"""
from __future__ import unicode_literals

from tx_lobbying.models import Interest


if __name__ == '__main__':
    import django; django.setup()  # ugh
    # print Interest.objects.count()
    # print Interest.objects.filter(canonical__isnull=True).count()
    qs = Interest.objects.filter(canonical__isnull=True, aliases__isnull=True)
    for x in qs:
        print x
