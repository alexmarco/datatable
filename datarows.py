# -*- coding: utf-8 -*-
"""Module for create DataRows objects.

A 'DataRow' object is a mutable data container with the ability to consume
less memory that dicts or class instances. In essence is like 'namedtuple' but
mutable.

Inspired by 'namedlist' package.
"""

import sys
import json
import collections

__version__ = '0.0.1a1'
__all__ = ['datarow_factory']

###############################################################################
# Blocks of the Class
###############################################################################


def __init__(self, *args, **kwargs):
    self.update(*args, **kwargs)


def __len__(self):
    return self.slots_length


def __getitem__(self, item):
    if isinstance(item, slice):
        return [getattr(self, x) for x in self.__slots__[item]]
    else:
        return getattr(self, self.__slots__[item])


def __iter__(self):
    for item in self.__slots__:
        if hasattr(self, item):
            yield item, getattr(self, item)


def __eq__(self, other):
    try:
        return tuple(self) == tuple(other)
    except TypeError:
        return False


def __ne__(self, other):
    return not self.__eq__(other)


def __contains__(self, attr):
    return attr in self.__slots__


def __hash__(self):
    return hash(tuple(self))


def __repr__(self):
    attr = ("%s=%r" % (k, v) for k, v in self)
    return u"%s(%s)" % (self.__class__.__name__, ', '.join(attr))


def __getstate__(self):
    return dict((slot, getattr(self, slot))
                for slot in self.__slots__ if hasattr(self, slot))


def __setstate__(self, state):
    for slot, value in state.items():
        setattr(self, slot, value)


def __dict__(self):
    return self.todict()


def _hash(self):
    # hash() only work with strings
    return hash(self.json())


def _get(self, attr, default=None):
    return getattr(self, attr, default)


def _attrget(self, *attr):
    u"""Recreate object with selected attributes."""
    return datarow_factory(*attr)(*[self.get(x) for x in attr])


def _todict(self):
    u"""Return unordered dict."""
    return dict(tuple(self))


def _keys(self):
    u"""Get keys from object."""
    return tuple(self.__slots__)


def _values(self):
    u"""Get values from object."""
    return tuple(v for k, v in self)


def _find(self, attr):
    return self.__slots__.index(attr)


def _json(self):
    """"""
    return json.dumps(vars(self))


###############################################################################
# Class factory
###############################################################################


def datarow_factory(*fields, **factory_kwargs):
    u"""Factory function that generate a *DataRow* class.

    Generate *DataRow* class with the given fields. Default value can be
    passed for attributes.

    Args:
        *fields: list of named fields. Only permited regular attribute names.
        **factory_kwargs: variable keyword. Now, only for pass *default_value*.

    Returns:
        *DataRow*: Returns a *DataRow* class with the attribute names specified
            in the factory (*fields argument).
    """

    if not fields:
        raise ValueError(u"Param 'fields' not found")

    # **factory_kwargs
    default_value = factory_kwargs.pop('default_value', None)
    name = factory_kwargs.pop('name', 'DataRow')
    if factory_kwargs:
        raise ValueError(
            "Unexpected keyword arguments: '{}'".format(factory_kwargs))

    def _update(self, *args, **kwargs):
        total_args = len(args) + len(kwargs)
        if total_args > self.slots_length:
            raise ValueError(u"Number of fields incorrect ('{}' > '{}')."
                             .format(total_args, self.slots_length))
        slots = list(self.__slots__)
        for slot, arg in zip(self.__slots__, args):
            setattr(self, slot, arg)
            slots.remove(slot)

        for attr in slots:
            try:
                setattr(self, attr, kwargs[attr])
            except KeyError:
                value = getattr(self, attr, default_value)
                setattr(self, attr, value)

    def _clear(self):
        for k in self.__slots__:
            setattr(self, k, default_value)

    def from_json(cls, json_data):
        u"""Create *DataRow* object from json data."""
        init_data = json.loads(json_data)
        return cls(**init_data)

    cls = {
        'from_json': classmethod(from_json),
        '__slots__': fields,
        'slots_length': len(fields),
        '__init__': __init__,
        '__len__': __len__,
        '__getitem__': __getitem__,
        '__iter__': __iter__,
        '__eq__': __eq__,
        '__ne__': __ne__,
        '__contains__': __contains__,
        '__hash__': __hash__,
        '__repr__': __repr__,
        '__getstate__': __getstate__,
        '__setstate__': __setstate__,
        '__dict__': property(__dict__),
        'clear': _clear,
        'hash': property(_hash),
        'update': _update,
        'get': _get,
        'attrget': _attrget,
        'todict': _todict,
        'keys': _keys,
        '_fields': fields,
        'values': _values,
        'find': _find,
        'json': _json
    }

    # Code from namedtuple
    try:
        cls['__module__'] = sys._getframe(1).f_globals.get('__name__',
                                                           '__main__')
    except (AttributeError, ValueError):
        pass

    cls = type(name, (object,), cls)

    collections.MutableSequence.register(cls)

    return cls
