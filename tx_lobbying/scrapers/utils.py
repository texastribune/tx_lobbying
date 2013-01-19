def convert_date_format(str):
    """Convert 12/25/2009 to 2009-12-25."""
    # TODO convert to Date so we can do comparisons
    month, day, year = str.split('/')
    return u"-".join([year, month, day])


def setfield(obj, fieldname, value):
    """Fancy setattr."""
    old = getattr(obj, fieldname)
    if old != value:
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
        obj._is_dirty.append("%s %s->%s" % (fieldname, old, value))
