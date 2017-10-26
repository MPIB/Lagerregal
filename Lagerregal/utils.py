import csv, codecs, cStringIO
import uuid
from datetime import date, timedelta
from django.conf import settings
from django.test.runner import DiscoverRunner

class PaginationMixin():
    def get_paginate_by(self, queryset):
        if self.request.user.pagelength == None:
            return self.request.user.pagelength
        else:
            return 30

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def get_file_location(instance=None, filename=""):

    destination = ""

    if instance:
        destination += instance.__class__.__name__.lower()

    destination += "/"
    ext = filename.split(".")[-1]
    destination += "{0}.{1}".format(uuid.uuid4(), ext)

    return destination


def convert_ad_accountexpires(timestamp):
    """
    returns a datetime.date object
    returns None when timestamp is 0, larger than date.max or on another error
    """
    if timestamp is None or timestamp == 0:
        return None
    epoch_start = date(year=1601, month=1,day=1)
    seconds_since_epoch = timestamp/10**7
    try:
        # ad timestamp can be > than date.max, return None (==never expires)
        new_date = epoch_start + timedelta(seconds=seconds_since_epoch)
        return new_date
    except OverflowError:
        return None
    except StandardError:
        print('Cannot convert expiration_date "{0}", falling back to None'.format(self.expiration_date))


class DetectableTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        settings.TEST_MODE = True
        super(DetectableTestRunner, self).__init__(*args, **kwargs)
