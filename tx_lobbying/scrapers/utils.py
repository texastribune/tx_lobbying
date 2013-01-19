import datetime


def convert_date_format(str):
    """Convert 12/25/2009 to date object."""
    # TODO convert to Date so we can do comparisons
    month, day, year = str.split('/')
    return datetime.date(int(year), int(month), int(day))


def setfield(obj, fieldname, value):
    """Fancy setattr."""
    old = getattr(obj, fieldname)
    if old != value:
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
        obj._is_dirty.append("%s %s->%s" % (fieldname, old, value))
