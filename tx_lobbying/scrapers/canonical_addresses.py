#!/usr/bin/env python
from tx_lobbying.utils import update_addresses


if __name__ == '__main__':
    import django
    django.setup()
    update_addresses()
