import sqlite3
from db_setup import db_filename

# connect to the database
def make_connection():
    conn = sqlite3.connect(db_filename)
    cur = conn.cursor()
    return (conn, cur)


# a very not safe way to create SQL commands
# CREATE TABLE table_name (column type etc, column type);
def create_table_command(table_name, column_data):
    command = 'CREATE TABLE '
    command += table_name
    command += ' ( '
    first = True
    for key, value in column_data.items():
        if not first:
            command += ', '
        else:
            first = False
        command += key + ' '
        # command += ' '
        for thing in value:
            command += thing + ' '
    command += ');'
    return command

# INSERT INTO table_name (column1, column2, ...) VALUES (? , ?, ...);
def insert_into_command(table_name, columns):
    command = 'INSERT INTO '
    command += table_name
    command += ' ('
    first = True
    for column in columns:
        if not first:
            command += ', '
        else:
            first= False
        command += column + ' '
    command += ') VALUES ('
    first = True
    for _ in columns:
        if not first:
            command += ', '
        else:
            first = False
        # command += str(value) + ' '
        command += '? '
    command += ');'
    return command

# UPDATE table_name SET columns[0] = ?, columns[1] = ?, ... WHERE rowid = rowid;
def update_command_w_rowid(table_name, columns):
    command = 'UPDATE ' + table_name + ' SET '
    first = True
    for column in columns:
        if not first:
            command += ', '
        else:
            first = False
        command += column + ' = ? '
    command += ' WHERE rowid = ?;'
    return command


# SELECT columns[0], columns[1], ... FROM table_name;
def select_column_command(table_name, columns):
    # command = 'SELECT ' + column_name + ' FROM ' + table_name + ';'
    command = 'SELECT '
    first = True
    for column in columns:
        if not first:
            command += ', '
        command += column
        if first:
            first = False
    command += ' FROM ' + table_name + ';'
    return command


# column_data as a dict with column name as key, type etc as value (tuple/list)
def create_table(table_name, column_data):
    conn = make_connection()[0]
    with conn:
        command = create_table_command(table_name, column_data)
        try:
            conn.execute(command)
        except sqlite3.OperationalError:
            print('Table', table_name, 'exists already')
    # conn.commit()
    conn.close()

# insert data to specific columns
def insert_data(table_name, columns, data):
    conn = make_connection()[0]
    with conn:
        command = insert_into_command(table_name, columns)
        # print(command)
        conn.execute(command, data)
    conn.close()

# insert data to a table which may or may not exist
def insert_data_and_create_table_if_not_created(table_name, column_data, data):
    try:
        insert_data(table_name, column_data.keys(), data)
    # this can fail badly if there is another operationalerror...
    except sqlite3.OperationalError:
        create_table(table_name, column_data)
        insert_data(table_name, column_data.keys(), data)

# update data in specific columns in a row given by rowid
def update_data_by_rowid(table_name, columns, new_data, rowid):
    conn = make_connection()[0]
    with conn:
        command = update_command_w_rowid(table_name, columns)
        data = list(new_data)
        data.append(rowid)
        conn.execute(command, data)
    conn.close()

# get everything in specific columns
def select_columns(table_name, columns):
    conn, cur = make_connection()
    with conn:
        command = select_column_command(table_name, columns)
        cur.execute(command)
        data = cur.fetchall()
    return data

# get everything from table_name
def select_all(table_name):
    conn, cur = make_connection()
    with conn:
        cur.execute('SELECT rowid, * FROM ' + table_name)
        all_things = cur.fetchall()
    return all_things

# get info on row with specific rowid
def select_row_by_rowid(table_name, rowid):
    conn, cur = make_connection()
    with conn:
        command = 'SELECT rowid, * FROM ' + table_name + ' WHERE rowid = ?;'
        cur.execute(command, (rowid,))
        row = cur.fetchone()
    return row

# get info on rows with column = value
def select_rows_by_column_value(table_name, column, value):
    conn, cur = make_connection()
    with conn:
        command = 'SELECT rowid, * FROM ' + table_name + ' WHERE ' + column + ' = ?;'
        cur.execute(command, (value,))
        rows = cur.fetchall()
    return rows



