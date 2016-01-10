# -*- coding: utf-8 -*-
import pytest
import types

from . import test_csv
from .._utils import SDict
from ..datatables import DataTable
from ..datatables import (DataTableError, DataTableColumnError,
                          DataTableCapacityError)


matrix_1 = [(0, 1, 2, 3, 4),
            (5, 6, 7, 7, 8),
            (9, 10, 11, 12, 13),
            (14, 15, 16, 17, 18),
            (19, 20, 21, 22, 23)]

###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def raw_container():
    tcsv = test_csv[:]
    dt = DataTable(*tcsv, firstrow_header=True)
    return dt


@pytest.fixture
def test_csv_data_container():
    tcsv = test_csv[:]
    fieldnames = tcsv.pop(0)
    return [SDict(zip(fieldnames, x)) for x in tcsv]


###############################################################################
# Test section: Void object
###############################################################################

dt = DataTable()


def test_create_datatable():
    assert isinstance(dt, DataTable)


def test_length():
    assert len(dt) == 0
    assert dt.count == 0


def test_initialized():
    assert dt.is_initialized is False

###############################################################################
# Test section: Basic tests
###############################################################################


def test_init_data():
    dt = DataTable(['hello', 'world!'])
    assert len(dt) == 1
    assert dt.count == 1
    assert dt.shape == (2, 1)
    assert dt.colnames == ('C0', 'C1')


#TODO(Alejandro): Test all the keyword parameters
def test_keyword_arguments():
    dt = DataTable(*[['header1'], ['hello']],
                   name='test_datatable',
                   firstrow_header=True)
    assert dt.name == 'test_datatable'
    assert dt.colnames == ('header1',)


def test_unexpected_keyword_arguments():
    with pytest.raises(DataTableError):
        DataTable(['hello'], unexpected=1)


def test_checker_capacity(raw_container):
    dt = DataTable(capacity=2)
    dt.append(['hello'])
    dt.append(['world!'])
    with pytest.raises(DataTableCapacityError):
        dt.append(['raises'])


def test_count():
    dt = DataTable()
    dt.extend(matrix_1)
    assert dt.count == 5


def test_unicode_colnames():
    dt = DataTable(colnames=(u'caño', 'two'))
    assert dt.colnames == (u'caño', 'two')


def test_getitem():
    dt = DataTable(['hello', 'world!'])
    assert dt[0] == ('hello', 'world!')


def test_getitem_column():
    dt = DataTable(*[['header_1', 'header_2'],
                     ['hello', 'world!']], firstrow_header=True)
    assert dt['header_1'] == ('header_1', 'hello')


def test_getitem_bad_column():
    dt = DataTable(*[['header_1', 'header_2'],
                     ['hello', 'world!']], firstrow_header=True)
    with pytest.raises(DataTableColumnError):
        dt['header_']


def test_insert():
    dt = DataTable(['hello', 'world!'])
    dt.insert(0, ['header_1', 'header_2'])
    assert dt[0] == ('header_1', 'header_2')


def test_append_items():
    dt = DataTable()
    dt.append(['hello'])
    assert len(dt) == 1


def test_setitem():
    dt = DataTable(['hello'])
    dt[0] = ['hello!']
    assert dt[0] == ('hello!',)


def test_setitem_no_index():
    dt = DataTable()
    with pytest.raises(IndexError):
        dt[0] == ['hello']


def test_pop():
    dt = DataTable(*[['hello'], ['world!']])
    assert dt.count == 2
    dt.pop()
    assert dt.count == 1
    assert dt[0] == ('hello',)


def test_reverse():
    dt = DataTable(*[['hello'], ['world!']])
    assert dt[0] == ('hello',)
    dt.reverse()
    assert dt[0] == ('world!',)


def test_extend():
    dt = DataTable()
    dt.extend([["item %i" % x] for x in range(10)])
    assert len(dt) == 10


def test_delete_item():
    dt = DataTable(['hello'])
    assert dt.count == 1
    del dt[0]
    assert dt.count == 0


def test_slice_delete(raw_container):
    dt = raw_container
    assert dt.count == 25
    del dt[:5]
    assert dt.count == 20


def test_iadd_operator():
    dt = DataTable(*['hello']*10)
    assert dt.count == 10
    a = ['world!']*10
    dt += a
    assert dt.count == 20


def test_iadd_operator_same_object():
    dt = DataTable(*['hello']*10)
    assert dt.count == 10
    dt += dt
    assert dt.count == 20


def test_add_operator():
    dt = DataTable(*['hello']*10)
    assert dt.count == 10
    a = ['world!']*10
    dt + a
    assert dt.count == 20


def test_add_operator_same_object():
    dt = DataTable(*['hello']*10)
    assert dt.count == 10
    dt + dt
    assert dt.count == 20


def test_shape():
    dt = DataTable(*matrix_1)
    assert dt.shape == (5, 5)


def test_representation():
    dt = DataTable(['hello', 'world!'])
    assert list(dt) == [('hello', 'world!')]
    assert str(dt) == "[('hello', 'world!')]"
    assert repr(dt) == "DataTable([('hello', 'world!')])"

    dt = DataTable(*matrix_1)
    assert str(dt) == str(matrix_1)
    assert repr(dt) == "DataTable(%s)" % matrix_1


def test_colnames():
    dt = DataTable(*[[1, 2], [3, 4]], colnames=('one', 'two'))
    assert dt.colnames == ('one', 'two')
    with pytest.raises(TypeError):
        dt.colnames = 'one'


def test_filter(raw_container):
    dt = raw_container

    def filter_fnc(row):
        return row.first_name.startswith('P')

    r = dt.filter(filter_fnc)
    assert r.count == 3
    assert isinstance(r, DataTable)


def test_filter_lambda(raw_container):
    dt = raw_container
    r = dt.filter(lambda row: row.first_name.startswith('P'))
    assert r.count == 3
    assert isinstance(r, DataTable)


# def test_filter_expr(raw_container):
#     dt = raw_container
#     r = dt.filter("row.first_name.startswith('P')")
#     assert r.count == 3
#     assert isinstance(r, DataTable)


def test_filter_chained(raw_container):
    dt = raw_container
    r = (dt
         .filter(lambda row: row.first_name.startswith('P'))
         .filter(lambda row: row.id == '10'))
    assert r.count == 1
    assert isinstance(r, DataTable)


# # Select testing


def test_select(raw_container):
    dt = raw_container
    dtn = dt.select('ip_address')
    assert isinstance(dtn, DataTable)
    assert dtn.colnames == ('ip_address',)
    assert dtn.count == 25
    assert dtn[0] == ('222.104.189.193',)


def test_select_unordered_fields(raw_container):
    dt1 = raw_container.select('id', 'ip_address')
    assert dt1.colnames == ('id', 'ip_address')
    assert dt1.count == 25
    assert dt1[0] == ('1', '222.104.189.193')
    assert raw_container.colnames == ('id', 'first_name', 'last_name',
                                      'email', 'gender', 'ip_address')

    dt2 = raw_container.select('ip_address', 'first_name', 'gender')
    assert dt2.colnames == ('ip_address', 'first_name', 'gender')
    assert dt2.count == 25
    assert dt2[0] == ('222.104.189.193', 'Diane', 'Female')


def test_select_no_string_fields(raw_container):
    dt = raw_container
    with pytest.raises(DataTableColumnError):
        dt.select(1)


def test_select_field_not_found(raw_container):
    dt = raw_container
    with pytest.raises(DataTableColumnError):
        dt.select('not_found')


def test_select_with_no_fields(raw_container):
    dt = raw_container
    assert dt.select() is dt


def test_select_with_conditions(raw_container):
    dt = raw_container
    assert dt.select('ip_address',
                     where=lambda row: not row.ip_address).count == 2


def test_chained_select0(raw_container):
    dt = raw_container

    def cond_expr(row):
        return row.gender == 'Male' and row.first_name.endswith('s')

    r = (
        dt
        .select('id', 'first_name', 'gender', 'ip_address', where=cond_expr)
        .select('id', 'ip_address')
    )

    assert list(r) == [('5', '7.106.49.156')]


def test_distinct(raw_container):
    dt = raw_container + raw_container
    assert dt.distinct().count == 25


def test_distinct_with_fields(raw_container):
    dt = raw_container
    assert dt.distinct('first_name').count == 23


def test_dup(raw_container):
    dt = raw_container + raw_container
    assert dt.dup().count == 25


def test_dup_with_fields(raw_container):
    dt = raw_container
    assert dt.dup('first_name').count == 2


def test_add_field(raw_container):
    dt = raw_container
    dtn = dt.add_field('test', 'add_field_test')
    assert isinstance(dtn, DataTable)
    assert dtn.colnames == ('id', 'first_name', 'last_name', 'email',
                            'gender', 'ip_address', 'test')
    assert dtn[0][-1] == 'add_field_test'


def test_add_field_index(raw_container):
    dt = raw_container
    dtn = dt.add_field('test', 'add_field_test', index=2)
    assert isinstance(dtn, DataTable)
    assert dtn.colnames == ('id', 'first_name', 'test', 'last_name', 'email',
                            'gender', 'ip_address')
    assert dtn[0][2] == 'add_field_test'


def test_add_field_callable(raw_container):
    dt = raw_container
    dtn = dt.add_field('test_calculated_field',
                       lambda row: row.id + ':' + row.ip_address)
    assert isinstance(dtn, DataTable)
    assert dtn.colnames == ('id', 'first_name', 'last_name', 'email',
                            'gender', 'ip_address', 'test_calculated_field')
    assert dtn[0][-1] == '1:222.104.189.193'


def test_add_field_callable_chain(raw_container):
    dt = raw_container
    dtn = dt \
          .add_field('test_calculated_field',
                     lambda row: row.id + ':' + row.ip_address) \
          .add_field('Initial', lambda row: row.first_name[0]) \
          .select('id', 'Initial')
    assert isinstance(dtn, DataTable)
    assert dtn[0] == ('1', 'D')
