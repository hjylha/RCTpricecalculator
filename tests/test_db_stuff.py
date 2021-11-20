import fix_imports

import db_stuff
from db_stuff import DB_general


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

# data = DB_general.column_data_as_string(DB_general.master_table_columns_dict)

# # print(data)

# cols_and_data = DB_general.prepare_to_add_to_master_table(DB_general.master_table_name, DB_general.master_table_columns_dict)

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