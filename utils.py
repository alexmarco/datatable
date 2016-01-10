
from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass


def total_size(o, handlers={}, verbose=False, readable_output=True):
    """Returns the memory footprint (aprox.) an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    #TODO(alexmarco): put credits of this function (ActiveState CookBook).

    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {
        tuple: iter,
        list: iter,
        deque: iter,
        dict: dict_handler,
        set: iter,
        frozenset: iter
    }
    # user handlers take precedence
    all_handlers.update(handlers)
    # track which object id's have already been seen
    seen = set()
    # estimate sizeof object without __sizeof__
    default_size = getsizeof(0)

    def sizeof(o):
        # do not double count the same object
        if id(o) in seen:
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    if readable_output:
        return sizeof_fmt(sizeof(o))
    return sizeof(o)


def sizeof_fmt(num, suffix='B'):
    """Format size data in human readable."""
    #TODO(alexmarco): put credits of this function (stackoverflow).
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


class SDict(object):
    """Create objects accessed by attribute or by item.
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return ((k, v) for k, v in self.__dict__.items())

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        kvp = ["%s=%r" % x for x in self.__dict__.items()]
        return "Data(%s)" % ', '.join(kvp)

    def __str__(self):
        return self.__dict__


def encode(data, encoding='utf-8'):
    """Return data encoded (recursive function).
    """
    if isinstance(data, basestring):
        if not isinstance(data, unicode):
            return unicode(data, encoding)
        return data
    elif isinstance(data, (tuple, list)):
        return type(data)([encode(x, encoding) for x in data])
    else:
        return unicode(data)


suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


def size_fmt(nbytes):
    """Format size data in human readable."""
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
