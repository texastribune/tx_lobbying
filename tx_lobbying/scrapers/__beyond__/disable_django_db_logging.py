"""
Keeps django from logging sql queries. Prevents RAM from filling up.

http://stackoverflow.com/questions/7768027/turn-off-sql-logging-while-keeping-settings-debug
"""
from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper

BaseDatabaseWrapper.make_debug_cursor = \
    lambda self, cursor: CursorWrapper(cursor, self)
