import sqlite3

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


# database class
class DB:
    # initialize just by giving the location of the database, and maybe table_data as a dict
    def __init__(self, filepath_of_db, table_data=None) -> None:
        self.filepath = filepath_of_db
        if table_data is not None:
            self.tables = table_data
        else:
            self.tables = dict()

    # connect to database
    def connect(self):
        conn = sqlite3.connect(self.filepath)
        cur = conn.cursor()
        return conn, cur

    # create a new table
    # column_data as a dict with column name as key, type etc as value (tuple/list)
    def create_table(self, table_name, column_data):
        if column_data is None:
            return
        conn = self.connect()[0]
        with conn:
            command = create_table_command(table_name, column_data)
            try:
                conn.execute(command)
            except sqlite3.OperationalError:
                # I guess there could be other errors, but...
                print('Table', table_name, 'already exists')
        conn.close()
        # self.tables[table_name] = column_data
    
    # create all the tables according to self.tables
    def create_tables(self):
        for table in self.tables:
            self.create_table(table, self.tables[table])

    # insert data to specific columns
    def insert(self, table_name, columns, data):
        conn = self.connect()[0]
        with conn:
            command = insert_into_command(table_name, columns)
            conn.execute(command, data)
        conn.close()

    def insert_and_create_table_if_needed(self, table_name, column_data, data):
        try:
            self.insert(table_name, column_data.keys(), data)
        except sqlite3.OperationalError:
            self.create_table(table_name, column_data)
            self.insert(table_name, column_data.keys(), data)

    # update data in specific columns in a row given by rowid
    def update_by_rowid(self, table_name, columns, new_data, rowid):
        conn = self.connect()[0]
        with conn:
            command = update_command_w_rowid(table_name, columns)
            data = list(new_data)
            data.append(rowid)
            conn.execute(command, data)
        conn.close()

    # get everything in specific columns
    def select_columns(self, table_name, columns):
        conn, cur = self.connect()
        with conn:
            command = select_column_command(table_name, columns)
            try:
                cur.execute(command)
                data = cur.fetchall()
            except sqlite3.OperationalError:
                # presumably table or columns do not exist?
                data = None
        return data

    # get everything from a table
    def select_all(self, table_name):
        conn, cur = self.connect()
        with conn:
            try:
                cur.execute('SELECT rowid, * FROM ' + table_name)
                all_things = cur.fetchall()
            except sqlite3.OperationalError:
                # table_name not found, presumably
                all_things = None
        return all_things
    
    # get everything in tables referenced in self.tables
    def get_everything(self):
        everything = dict()
        for table in self.tables:
            everything[table] = self.select_all(table)
        return everything

    # get info on rows with column = value
    def select_rows_by_column_value(self, table_name, column, value):
        conn, cur = self.connect()
        with conn:
            command = 'SELECT rowid, * FROM ' + table_name + ' WHERE ' + column + ' = ?;'
            cur.execute(command, (value,))
            rows = cur.fetchall()
        return rows
    
    # get info on row with specific rowid
    def select_row_by_rowid(self, table_name, rowid):
        rows = self.select_rows_by_column_value(table_name, 'rowid', rowid)
        return rows[0]


