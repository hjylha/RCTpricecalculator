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
    columns_w_condition = ('rowid',)
    command = 'UPDATE Table_Name SET column1 = ?, column2 = ? WHERE rowid = ?;'
    assert db_stuff.update_command_w_where(table, columns, columns_w_condition) == command


def test_select_column_command():
    table = 'Table_Name'
    columns = ('column1', 'column2')
    command = 'SELECT column1, column2 FROM Table_Name;'
    assert db_stuff.select_column_command(table, columns) == command

def test_select_columns_where_command():
    table = 'Table_Name'
    columns = ('column1', 'column2')
    columns_w_cond = ('column3', 'column4')
    command = 'SELECT column1, column2 FROM Table_Name WHERE column3 = ?, column4 = ?;'
    assert db_stuff.select_columns_where_command(table, columns, columns_w_cond) == command


# testing DG_general

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

def test_DB_general():
    pass

data = DB_general.column_data_as_string(DB_general.master_table_columns)

print(data)

cols_and_data = DB_general.prepare_to_add_to_master_table(DB_general.master_table_name, DB_general.master_table_columns)

print('cols_and_data:')
print(cols_and_data[0])
print(cols_and_data[1])

col_data = DB_general.string_to_column_data(data)
for item in col_data:
    print(item, col_data[item])


db = DB_general('test.db')
everything = db.get_everything()
print(len(everything))

table_test = 'test'
col_data = {'first': ('TEXT', 'NOT NULL', 'UNIQUE'), 'second': ('TEXT',)}