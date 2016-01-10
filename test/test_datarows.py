# -*- coding: utf-8 -*-
import json
import pickle
import pytest

from operator import itemgetter, attrgetter

from ..datarows import datarow_factory


# Clases for testing
DataRow = datarow_factory('test_a', 'test_b', 'test_c')
UDataRow = datarow_factory(u'test_a', u'test_b', u'test_c')


def test_bad_init():
    """Create class with bad args."""
    with pytest.raises(ValueError):
        # no arguments
        datarow_factory()
    with pytest.raises(TypeError):
        # ilegal characters
        datarow_factory('Hello world!')
    with pytest.raises(TypeError):
        # non ascii chars in field names
        datarow_factory('caño')
    with pytest.raises(TypeError):
        # no string field names
        datarow_factory(1, 2, 3)
    with pytest.raises(ValueError):
        # unknown keyword arguments
        datarow_factory('one', name='Test', bad=0)


def test_default_class_name():
    dr = DataRow()
    assert isinstance(dr, DataRow)
    assert dr.__class__.__name__ == 'DataRow'


def test_class_name():
    Row = datarow_factory('col_a', 'col_b', name='Row')
    row = Row()
    assert isinstance(row, Row)
    assert row.__class__.__name__ == 'Row'


def test_slots_length():
    assert DataRow.slots_length == 3


def test_init_instance_with_keyword():
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert dr.test_a == 'hello_a'
    assert dr.test_b == 'hello_b'
    assert dr.test_c is None


def test_init_instance_with_dict():
    dr = DataRow(**{'test_a': 'hello_a', 'test_c': 'hello_c'})
    assert dr.test_a == 'hello_a'
    assert dr.test_b is None
    assert dr.test_c == 'hello_c'


def test_unicode_attr():
    assert UDataRow.__slots__ == (u'test_a', u'test_b', u'test_c')


def test_unicode_values():
    dr = UDataRow(test_a=u'caño_a')
    assert dr.test_a == u'caño_a'


def test_keys():
    dr = DataRow()
    assert dr.keys() == ('test_a', 'test_b', 'test_c')


def test_values():
    dr = DataRow('one', 'two')
    assert dr.values() == ('one', 'two', None)


def test_default_values():
    dr = DataRow('one')
    assert dr.values() == ('one', None, None)


def test_index_access():
    dr = DataRow('hello_a', 'hello_b')
    assert dr[0] == 'hello_a'
    assert dr[1] == 'hello_b'
    assert dr[2] is None


def test_slice_access():
    dr = DataRow('one', 'two', 'three')
    assert dr[1:3] == ['two', 'three']


def test_get():
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert dr.get('test_d', 'test_no_exists') == 'test_no_exists'


def test_vars():
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert vars(dr) == dr.todict()


def test_hash():
    dr_a = DataRow(test_a='hello_a', test_b='hello_b')
    dr_b = DataRow(test_a='hello_a', test_b='hello_b')
    assert dr_a.hash is not None
    assert dr_a.hash == dr_b.hash

    dr_a.update(test_a=1)
    assert dr_a.hash != dr_b.hash


def test_todict():
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert dr.todict() == {'test_a': 'hello_a',
                           'test_b': 'hello_b',
                           'test_c': None}


def test_itemgetter():
    getter = itemgetter(0, 2)
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert getter(dr) == (dr[0], dr[2])


def test_attrgetter():
    getter = attrgetter('test_a', 'test_c')
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert getter(dr) == (dr.test_a, dr.test_c)


def test_update():
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    dr.update(test_a='updated_attr_a', test_c='hello_c')
    assert dr.test_a == 'updated_attr_a'
    assert dr.test_b == 'hello_b'
    assert dr.test_c == 'hello_c'

    dr = DataRow(test_a='hello_a', test_b='hello_b')
    dr.update(**{'test_a': 'updated_attr_a', 'test_b': 'updated_hello_b'})
    assert dr.test_a == 'updated_attr_a'
    assert dr.test_b == 'updated_hello_b'
    assert dr.test_c is None


def test_clear_values():
    dr = DataRow('hello_a', 'hello_b')
    dr.clear()
    assert dr.values() == (None, None, None)


def test_tuple():
    dr = DataRow()
    assert tuple(dr) == (('test_a', None),
                         ('test_b', None),
                         ('test_c', None))

    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert tuple(dr) == (('test_a', 'hello_a'),
                         ('test_b', 'hello_b'),
                         ('test_c', None))


def test_repr():
    dr = DataRow()
    assert repr(dr) == "DataRow(test_a=None, test_b=None, test_c=None)"

    Row = datarow_factory('test_a', 'test_b', name='Row')
    dr = Row(test_b=[1, 2])
    assert repr(dr) == "Row(test_a=None, test_b=[1, 2])"


def test_contains():
    dr1 = DataRow()
    assert 'test_a' in dr1
    assert 'h' not in dr1


def test_compare():
    dr1 = DataRow('hello_a', 'hello_b')
    dr2 = DataRow('hello_a', None, 'hello_c')
    assert dr1 != dr2
    dr2 = DataRow('hello_a', 'hello_b')
    assert dr1 == dr2


def test_attrget():
    dr = DataRow('hello_a', 'hello_b')
    new_dr = dr.attrget('hello_b')
    assert new_dr.slots_length == 1
    assert hasattr(new_dr, 'hello_b')
    assert not hasattr(new_dr, 'hello_a')


def test_json():
    dr = DataRow(test_a='hello_a', test_b='hello_b')
    assert dr.json() == json.dumps({'test_a': 'hello_a',
                                    'test_b': 'hello_b',
                                    'test_c': None})


def test_create_from_json():
    json_data = json.dumps({'test_a': 'hello_a',
                            'test_b': {'nested_b': 3},
                            'test_c': None})
    dr = DataRow.from_json(json_data)
    assert dr == DataRow(test_a='hello_a', test_b={'nested_b': 3})


def test_pickle(tmpdir):
    dr1 = DataRow('hello_a', 'hello_b')
    dr2 = None
    with tmpdir.join('test_pickle.pic').open('w') as pic:
        pickle.dump(dr1, pic)

    with tmpdir.join('test_pickle.pic').open() as pic:
        dr2 = pickle.load(pic)

    assert dr1 == dr2

    pic_dr1 = pickle.dumps(dr1)
    dr2 = pickle.loads(pic_dr1)
    assert dr1 == dr2

# if __name__ == '__main__':

#     import sys
#     import psutil

#     from datetime import datetime
#     from collections import namedtuple
#     from namedlist import namedlist

#     from datastructs.test.test_utils import size_fmt

#     display_iter = 500000

#     p = psutil.Process()
#     init_memory_usage = p.get_memory_info()[0]

#     args = sys.argv[1:] or [None]
#     object_type = ''
#     iterations = 1000000
#     if sys.argv[1:]:
#         object_type = sys.argv[1]
#         try:
#             iterations = int(sys.argv[2])
#         except IndexError:
#             pass

#     cnt = []

#     start_time = datetime.now()
#     if object_type == 'datarow':
#         DataRow = datarow_factory('uno', 'dos', 'tres', 'cuatro')
#         #dr = DataRow()
#         print "- 'DataRow' objects ('%i' objects in memory)" % iterations
#         for _ in xrange(iterations):
#             if not _ % display_iter:
#                 print "  --> Iteration '%i'" % _
#             cnt.append(DataRow(uno='111', dos='222', tres='333', cuatro='444'))

#     elif object_type == 'dict':
#         print "- Python 'dict' objects ('%i' objects in memory)" % iterations
#         for _ in xrange(iterations):
#             if not _ % display_iter:
#                 print "  --> Iteration '%i'" % _
#             cnt.append(dict(uno='111', dos='222', tres='333', cuatro='444'))

#     elif object_type == 'namedtuple':
#         print "- 'namedtuple' objects ('%i' objects in memory)" % iterations
#         nt = namedtuple('NamedTuple', ['uno', 'dos', 'tres', 'cuatro'])
#         for _ in xrange(iterations):
#             if not _ % display_iter:
#                 print "  --> Iteration '%i'" % _
#             cnt.append(nt(uno='111', dos='222', tres='333', cuatro='444'))

#     elif object_type == 'namedlist':
#         print "- 'namedlist' objects ('%i' objects in memory)" % iterations
#         nl = namedlist('NamedTuple', ['uno', 'dos', 'tres', 'cuatro'])
#         for _ in xrange(iterations):
#             if not _ % display_iter:
#                 print "  --> Iteration '%i'" % _
#             cnt.append(nl(uno='111', dos='222', tres='333', cuatro='444'))

#     elif object_type == 'instance':
#         print "- 'instance' objects ('%i' objects in memory)" % iterations

#         class Container(object):
#             def __init__(self, *args, **kwargs):
#                 self.__dict__.update(*args, **kwargs)

#         for _ in xrange(iterations):
#             if not _ % display_iter:
#                 print "  --> Iteration '%i'" % _
#             cnt.append(Container(uno='111', dos='222', tres='333',
#                                  cuatro='444'))

#     elapsed_time = (datetime.now() - start_time).total_seconds()
#     memory = p.get_memory_info()[0] - init_memory_usage
#     print "- Elapsed time: %.4f seconds, Memory: %s" % (elapsed_time,
#                                                         size_fmt(memory))
