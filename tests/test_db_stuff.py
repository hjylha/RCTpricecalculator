from pathlib import Path
import pytest

import fix_imports
import db_stuff
from db_stuff import DB_general


# testing fcns creating sql commands

def test_create_table_command():
    table = 'Table_Name'
    column_data = {'column1': ('TEXT', 'UNIQUE'), 'column2': ('INTEGER', 'NOT NULL')}
    command = 'CREATE TABLE Table_Name (column1 TEXT UNIQUE, column2 INTEGER NOT NULL);'
    assert db_stuff.create_table_command(table, column_data) == command


def test_insert_into_command():
    table = 'Table_Name'
    columns = ('column1', 'column2', 'column3')
    command = 'INSERT INTO Table_Name (column1, column2, column3) VALUES (?, ?, ?);'
    assert db_stuff.insert_into_command(table, columns) == command


def test_update_command_w_rowid():
    table = 'Table_Name'
    columns = ('column1', 'column2')
    command = 'UPDATE Table_Name SET column1 = ?, column2 = ? WHERE rowid = ?;'
    assert db_stuff.update_command_w_rowid(table, columns) == command

def test_update_command_w_where():
    table = 'Table_Name'
    columns = ('column1', 'column2')
    columns_w_condition = ('rowid', 'column1')
    command = 'UPDATE Table_Name SET column1 = ?, column2 = ? WHERE rowid = ? AND column1 = ?;'
    assert db_stuff.update_command_w_where(table, columns, columns_w_condition) == command


def test_select_column_command():
    table = 'Table_Name'
    columns = ('column1', 'column2')
    command = 'SELECT column1, column2 FROM Table_Name;'
    assert db_stuff.select_column_command(table, columns) == command

def test_select_columns_where_command():
    table = 'Table_Name'
    columns = ('column1', 'column2')
    columns_w_cond = ('column3', 'column4', 'column5')
    command = 'SELECT column1, column2 FROM Table_Name WHERE column3 = ? AND column4 = ? AND column5 = ?;'
    assert db_stuff.select_columns_where_command(table, columns, columns_w_cond) == command


# testing DG_general
@pytest.fixture
def db():
    db_path = Path('test_db.db')
    yield DB_general(db_path)
    db_path.unlink()


def test_master_table_columns():
    columns = DB_general.master_table_column_names
    assert columns == ('table_name', 'column_data')
    column_data = DB_general.master_table_columns
    assert column_data == {'table_name': ('TEXT', 'NOT NULL', 'UNIQUE'), 'column_data': ('TEXT', 'NOT NULL')}


def test_string_to_column_data():
    columns_as_str = '(table_name, (TEXT, NOT NULL, UNIQUE)), (column_data, (TEXT, NOT NULL))'
    column_data = DB_general.string_to_column_data(columns_as_str)
    assert column_data == DB_general.master_table_columns

def test_column_data_as_string():
    columns_as_str = '(table_name, (TEXT, NOT NULL, UNIQUE)), (column_data, (TEXT, NOT NULL))'
    column_data_as_str = DB_general.column_data_as_string(DB_general.master_table_columns)
    assert columns_as_str == column_data_as_str

def test_prepare_to_add_to_master_table():
    table = 'Table_Name'
    column_data = {'Col1': ('TEXT', 'UNIQUE')}
    result = DB_general.prepare_to_add_to_master_table(table, column_data)
    assert result[0] == ('table_name', 'column_data')
    assert result[1] == ('Table_Name', '(Col1, (TEXT, UNIQUE))')


def test_DB_general(db):
    # db = DB_general('test_db.db')
    assert 'tables' in db.tables
    assert set(['table_name', 'column_data']) == set(db.tables['tables'].keys())

def test_connect(db):
    conn, cur = db.connect()
    assert isinstance(conn, db_stuff.sqlite3.Connection)
    assert isinstance(cur, db_stuff.sqlite3.Cursor)
    conn.close()
    with pytest.raises(db_stuff.sqlite3.ProgrammingError):
        conn.in_transaction


def test_select_columns(db):
    table = 'tables'
    columns = ('table_name', 'column_data')
    column_data = db.select_columns(table, columns)
    row = ('tables', '(table_name, (TEXT, NOT NULL, UNIQUE)), (column_data, (TEXT, NOT NULL))')
    assert row in column_data

def test_select_columns_by_column_value(db):
    table = 'tables'
    columns = ('table_name',)
    columns_condition = ('table_name',)
    condition_value = ('tables',)
    selection = db.select_columns_by_column_value(table, columns, columns_condition, condition_value)
    assert table in selection[0]
    assert selection[0][0] == table

    columns = ('table_name', 'column_data')
    selection = db.select_columns_by_column_value(table, columns, columns_condition, condition_value)
    assert table in selection[0]
    assert 'table_name' in selection[0][1]

    columns_condition = ('table_name', 'column_data')
    condition_value = (table, '(table_name, (TEXT, NOT NULL, UNIQUE)), (column_data, (TEXT, NOT NULL))')
    assert table in selection[0]
    assert 'column_data' in selection[0][1]
    

def test_insert(db):
    table = 'tables'
    columns = ('table_name', 'column_data')
    data = ('test_name', 'not valid column data here')
    db.insert(table, columns, data)

    # select content and see if inserted data is there
    content = db.select_columns(table, columns)
    the_rows = [row for row in content if 'test_name' in row]
    assert the_rows[0][1] == 'not valid column data here'
    # not sure if it is necessary to remove this row, but let's do it anyway
    conn, cur = db.connect()
    with conn:
        cur.execute('DELETE FROM tables WHERE table_name = ? AND column_data = ?', data)
    conn.close()

def test_insert_many(db):
    table = 'tables'
    columns = ('table_name', 'column_data')
    search_name = 'searchable'
    data = (('name1', search_name), ('name2', search_name), ('name3', search_name))
    db.insert_many(table, columns, data)

    content = db.select_columns(table, columns)
    rows = [row for row in content if search_name in row]
    assert len(rows) == len(data)
    assert ['name1', 'name2', 'name3'] == [row[0] for row in rows]


def test_create_table(db):
    table = 'New_Table'
    column_data = {'Col1': ('TEXT', 'NOT NULL', 'UNIQUE'), 'Col2': ('INTEGER')}
    db.create_table(table, column_data)

    # this table should have been inserted to 'tables' table
    tables = db.select_columns_by_column_value('tables', ('table_name', 'column_data'), ('table_name',), (table,))
    assert table in tables[0]
    assert 'Col2' in tables[0][1]

    # it should also be in db.tables dictionary
    assert table in db.tables
    
    # try to insert something to this table
    columns = ('Col1', 'Col2')
    db.insert(table, columns, ('jee', 37))
    data = db.select_columns(table, ('Col1', 'Col2'))
    assert data[0] == ('jee', 37)

# fixture with an added table, and maybe some rows inserted
@pytest.fixture
def db1(db):
    # dbg = next(db())
    dbg = db
    table = 'test_table'
    column_data = {'Col1': ('TEXT',), 'Col2': ('TEXT',), 'Col3': ('INTEGER',)}
    dbg.create_table(table, column_data)
    columns = ('Col1', 'Col2', 'Col3')
    datalist = [('a', 'b', 1), ('c', 'd', 2), ('e', 'f', 3)]
    dbg.insert_many(table, columns, datalist)
    # create an empty table with same columns as above
    empty_table = 'empty_table'
    dbg.create_table(empty_table, column_data)
    return dbg

def test_get_table_data(db1):
    table_data = db1.get_table_data()
    assert 'tables' in table_data
    assert table_data == db1.tables
    # db1 tables should be in table_data
    assert 'empty_table' in table_data
    assert 'test_table' in table_data
    column_data = {'Col1': ('TEXT',), 'Col2': ('TEXT',), 'Col3': ('INTEGER',)}
    assert table_data['test_table'] == column_data


def test_update_by_rowid(db):
    pass

def test_update_by_column_value(db):
    pass

# less important fcns
def test_create_tables(db):
    pass

def test_insert_and_create_table_if_needed(db):
    pass

def test_select_rows_by_column_value(db):
    pass

def test_select_rows_by_text_wo_capitalization(db):
    pass

def test_select_row_by_rowid(db):
    pass

def test_select_all(db):
    pass

def test_get_everything(db):
    pass






# data = DB_general.column_data_as_string(DB_general.master_table_columns)

# print(data)

# cols_and_data = DB_general.prepare_to_add_to_master_table(DB_general.master_table_name, DB_general.master_table_columns)

# print('cols_and_data:')
# print(cols_and_data[0])
# print(cols_and_data[1])

# col_data = DB_general.string_to_column_data(data)
# for item in col_data:
#     print(item, col_data[item])


# db = DB_general('test.db')
# everything = db.get_everything()
# print(len(everything))

# table_test = 'test'
# col_data = {'first': ('TEXT', 'NOT NULL', 'UNIQUE'), 'second': ('TEXT',)}