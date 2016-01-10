# -*- coding: utf-8 -*-
"""

"""


import string
import operator
import collections

from itertools import imap, ifilter

from functools import wraps

from _utils import SDict
from _signals import Signal
#from datarows import datarow_factory


class DataTableError(Exception):
    pass


class DataTableCapacityError(DataTableError):
    pass


class DataTableColumnError(DataTableError):
    pass


class DataTableEventError(DataTableError):
    pass


class DataTableTypeError(DataTableError):
    pass


class Typed(object):
    """Base descriptor class."""
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("Expected %s (%s)"
                            % (self.expected_type, type(value)))
        instance.__dict__[self.name] = value


class ColnameDesc(Typed):
    expected_type = tuple


class NameDesc(Typed):
    expected_type = str


class CapacityDesc(Typed):
    expected_type = int


def get_datatype_name(cls):
    """"""
    if cls is None:
        return 'NoneType'
    s = str(cls.mro()[0])
    return ''.join(x for x in s.split()[-1].split('.')[-1]
                   if x in string.letters)


def is_attribute_access(obj, fields):
    """Check if object is accessed by attributes or not."""
    ag = operator.attrgetter(*fields)
    try:
        ag(obj)
        return True
    except AttributeError:
        return False


def fields2index(fields, data):
    out = []
    for f in fields:
        try:
            out.append(data.index(f))
        except ValueError:
            pass
    return out


def tuple_insert(data, index, value):
    return data[:index] + (value,) + data[index:]


###############################################################################
# Data functions
###############################################################################

def f_distinct(data):
    """Yield distinct rows."""
    seen = {}
    # convert to 'tuple' for storing in dict (need hashable object).
    for row in imap(tuple, data):
        if row in seen:
            continue
        seen[row] = 1
        yield row


def f_dup(data):
    """Yield duplicate rows."""
    seen = {}
    # convert to 'tuple' for storing in dict (need hashable object).
    for row in imap(tuple, data):
        if row in seen:
            yield row
            continue
        seen[row] = 1


def _look(data):
    for row in data:
        print "- ilook -> {}".format(row)
        yield row


###############################################################################
# Decorators
###############################################################################


def expr_decorator(method, colnames):
    def inner(row):
        sdict = SDict(zip(colnames, row))
        return method(sdict)
    return inner


def fluent(method):
    @wraps(method)
    def inner(self, *args, **kwargs):
        if (not self.is_initialized or
           (method.func_name.endswith('select') and not args)):
            return self
        # Instance creation
        obj = self.__class__.__new__(self.__class__)
        # method execution and new context
        result = method(self, *args, **kwargs)
        # Copy new context to new instance
        obj.__dict__ = self.__dict__.copy()
        if method.func_name == 'select':
            obj.colnames = args
        # Populate object
        obj.list = []
        obj.extend(result)
        return obj
    return inner


class DataTable(collections.MutableSequence):
    u"""Container class for store data.
    """

    colnames = ColnameDesc('colnames')
    name = NameDesc('name')
    capacity = CapacityDesc('capacity')

    def __init__(self, *args, **kwargs):

        self.colnames = kwargs.pop('colnames', ())
        """Column names."""
        self.name = kwargs.pop('name', 'data_table')
        """Store the name os the 'DataTable' object."""
        self.capacity = kwargs.pop('capacity', 0)
        """Store the max capacity of rows in the container."""
        self.firstrow_header = kwargs.pop('firstrow_header', False)
        """Identify if the firstrow is a header line."""
        # input_converter = kwargs.pop('input_converter', True)
        # """Disable input conversion to 'tuple' object (more speed)."""

        if kwargs:
            raise DataTableError("Unexpected keyword arguments (%r)" % kwargs)

        self.events = SDict(onAppend=Signal(), onInsert=Signal())

        if self.capacity:
            # Connect events to handlers.
            self.events.onAppend.append(self._capacity_checker)
            self.events.onInsert.append(self._capacity_checker)

        self.list = list()
        self.extend(args)

        if args and not self.colnames:
            if self.firstrow_header:
                self.colnames = tuple(self.list.pop(0))
            else:
                self.colnames = tuple("C%i" % x
                                      for x in range(len(self.list[0])))

    def __iter__(self):
        for row in self.list:
            yield row

    def __len__(self):
        return len(self.list)

    def __add__(self, value):
        if value is not self:
            self.extend(value)
        else:
            for row in self.list[:]:
                self.append(row)
        return self

    __iadd__ = __add__

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.list[item]
        elif isinstance(item, basestring):
            if item not in self.colnames:
                raise DataTableColumnError("Column '%s' not found" % item)

            idx = self.colnames.index(item)
            # Add header name in the first position
            l = (item,) + tuple(x[idx] for x in self.list)
            return l

    def __delitem__(self, index):
        def delitem(idx):
            del self.list[idx]
        if isinstance(index, slice):
            [delitem(i) for i in xrange(*index.indices(len(self)))]
        else:
            delitem(index)

    def __setitem__(self, index, row):
        # TODO(Alejandro): implement case when item is a 'slice'
        try:
            self.list[index] = tuple(row)
        except IndexError:
            raise DataTableError("Index '%i' not created" % index)

    def __repr__(self):
        return "DataTable(%s)" % self.list

    def __str__(self):
        return str(self.list)

    #
    # built-in event handlers.
    #

    def _capacity_checker(self):
        if self.count >= self.capacity:
            raise DataTableCapacityError(
                "Maximun capacity reached, stop ('%i')" % self.capacity)

    #
    # Special methods
    #

    def append(self, row):
        """"""
        self.events.onAppend()
        self.list.append(tuple(row))

    def insert(self, index, row):
        self.events.onInsert()
        self.list.insert(index, tuple(row))

    @fluent
    def filter(self, expr):
        u"""Filter container data."""
        data_kernel = self
        if not is_attribute_access(data_kernel[0], self.colnames):
            # Necessary for attribute access
            expr = expr_decorator(expr, self.colnames)
        return ifilter(expr, data_kernel)
        #return (x for x in data_kernel if expr(x))

    @fluent
    def select(self, *fields, **kwargs):
        u"""Select fields in the object."""
        if not all(isinstance(x, basestring) for x in fields):
            raise DataTableColumnError("Use only string types for parameter "
                                       "'fields'.")

        invalid_colnames = set(fields) - set(self.colnames)
        if invalid_colnames:
            raise DataTableColumnError("Column '%s' not found"
                                       % ', '.join(invalid_colnames))

        data_kernel = self
        where = kwargs.pop('where', lambda x: x)
        if not is_attribute_access(data_kernel[0], self.colnames):
            # Necessary for attribute access
            expr = expr_decorator(where, self.colnames)
        if len(fields) == 1:
            field_index = self.colnames.index(fields[0])
            getter = lambda row: (row[field_index],)
        else:
            getter = operator.itemgetter(*fields2index(fields, self.colnames))
        # getter transfor to tuples
        return imap(getter, ifilter(expr, data_kernel))

    @fluent
    def distinct(self, *fields):
        """Return new 'datatable' with distinct rows."""
        data_kernel = self
        if fields:
            data_kernel = self.select(*fields)
        return f_distinct(data_kernel)

    @fluent
    def dup(self, *fields):
        """Return new 'datatable' with distinct rows."""
        data_kernel = self
        if fields:
            data_kernel = self.select(*fields)
        return f_dup(data_kernel)

    @fluent
    def add_field(self, name, value='', index=-1):
        """"""
        if callable(value):
            expr = expr_decorator(value, self.colnames)
            data_kernel = (tuple_insert(row, index, expr(row)) for row in self)
        else:
            data_kernel = (tuple_insert(row, index, value) for row in self)

        if index == -1:
            index = len(self.colnames)

        self.colnames = tuple_insert(self.colnames, index, name)
        return data_kernel

    def clear(self, init=0, offset=0):
        u"""Clear object."""
        del self[init: init+offset]

    @property
    def is_initialized(self):
        u""""""
        return bool(self.count)

    @property
    def count(self):
        return len(self)

    @property
    def shape(self):
        rows = self.count
        cols = max(len(x) for x in self)
        return (cols, rows)
