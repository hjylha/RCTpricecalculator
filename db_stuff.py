import sqlite3

# connect to the database
def make_connection():
    conn = sqlite3.connect('rct_data.db')
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
        command += key + ' '
        # command += ' '
        for thing in value:
            command += thing + ' '
        if first:
            first = False
    command += ');'
    return command

# INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);
def insert_into_command(table_name, columns, data):
    command = 'INSERT INTO '
    command += table_name
    command += ' ('
    first = True
    for column in columns:
        if not first:
            command += ', '
        command += column + ' '
        if first:
            first = False
    command += ') VALUES ('
    first = True
    for value in data:
        if not first:
            command += ', '
        # command += str(value) + ' '
        command += '? '
        if first:
            first = False
    command += ');'
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

def insert_data(table_name, columns, data):
    conn = make_connection()[0]
    with conn:
        command = insert_into_command(table_name, columns, data)
        # print(command)
        conn.execute(command, data)
    conn.close()

# get everything from table_name
def select_all(table_name):
    conn, cur = make_connection()
    with conn:
        cur.execute('SELECT * FROM ' + table_name)
        all_things = cur.fetchall()
    return all_things



