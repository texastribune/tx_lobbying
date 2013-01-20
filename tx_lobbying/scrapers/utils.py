import codecs
import csv
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


# http://docs.python.org/2/library/csv.html#csv-examples
class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class DictReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.header = self.reader.next()

    def next(self):
        row = self.reader.next()
        vals = [unicode(s, "utf-8") for s in row]
        return dict((self.header[x], vals[x]) for x in range(len(self.header)))

    def __iter__(self):
        return self
