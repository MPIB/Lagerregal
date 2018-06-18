from __future__ import unicode_literals
import csv
import codecs
import uuid
from datetime import date, timedelta

import six
from django.conf import settings
from django.test.runner import DiscoverRunner

try:
    import io
except ImportError:
    import cStringIO as io


class PaginationMixin():
    def get_paginate_by(self, queryset):
        if self.request.user.pagelength is None:
            return self.request.user.pagelength
        else:
            return 30


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
    epoch_start = date(year=1601, month=1, day=1)
    seconds_since_epoch = timestamp/10**7
    try:
        # ad timestamp can be > than date.max, return None (==never expires)
        new_date = epoch_start + timedelta(seconds=seconds_since_epoch)
        return new_date
    except OverflowError:
        return None
    except Exception:
        print('Cannot convert expiration_date "{0}", falling back to None'.format(self.expiration_date))


class DetectableTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        settings.TEST_MODE = True
        super(DetectableTestRunner, self).__init__(*args, **kwargs)
