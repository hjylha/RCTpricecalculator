import sqlite3
from db_ini import get_column_names_for_table, get_columns_for_table

# a very not safe way to create SQL commands
# CREATE TABLE table_name (column type etc, column type);
def create_table_command(table_name, column_data):
    command = f'CREATE TABLE {table_name} ( '
    first = True
    for key, value in column_data.items():
        if not first:
            command += ', '
        else:
            first = False
        command += f'{key} '
        for thing in value:
            command += f'{thing} '
    command += ');'
    return command

# INSERT INTO table_name (column1, column2, ...) VALUES (? , ?, ...);
def insert_into_command(table_name, columns):
    command = f'INSERT INTO {table_name} ('
    first = True
    for column in columns:
        if not first:
            command += ', '
        else:
            first= False
        command += f'{column} '
    command += ') VALUES ('
    first = True
    for _ in columns:
        if not first:
            command += ', '
        else:
            first = False
        command += '? '
    command += ');'
    return command

# UPDATE table_name SET columns[0] = ?, columns[1] = ?, ... WHERE rowid = rowid;
def update_command_w_rowid(table_name, columns):
    command = f'UPDATE {table_name} SET '
    first = True
    for column in columns:
        if not first:
            command += ', '
        else:
            first = False
        command += f'{column} = ? '
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
    command += f' FROM {table_name};'
    return command


# database class
class DB_general:
    # db should have a table of tables
    master_table_name = 'tables'
    master_table_columns = get_columns_for_table(master_table_name, False)
    master_table_column_names = get_column_names_for_table(master_table_name)
    master_table_columns_dict = get_columns_for_table(master_table_name)
    # master_table_col_name = [col for col in master_table_columns if 'UNIQUE' in master_table_columns[col]][0]
    
    # how to read column data from master table
    @staticmethod
    def string_to_column_data(col_data_as_string):
        column_data = dict()
        text = col_data_as_string
        while text != '':
            # find the first instance of (,())
            bracket_count = 0
            index = len(text)
            for i, char in enumerate(text):
                if char == '(':
                    bracket_count += 1
                elif char == ')':
                    bracket_count -= 1
                    if bracket_count == 0:
                        index = i
                        break
            item_as_str = text[:index + 1]
            # get column name and data
            name_and_data = item_as_str.split('(')
            name = name_and_data[1].strip(', ')
            data = name_and_data[2].split(',')
            data = tuple(item.strip(")' ") for item in data)
            column_data[name] = data
            # make sure text starts with (
            try:
                text = text[index+1:].strip(', ')
            except IndexError:
                text = ''
        return column_data

    # how to store column data in master table
    @staticmethod
    def column_data_as_string(column_data: dict) -> str:
        text = ''
        first = True
        for column, value in column_data.items():
            if first:
                first = False
            else:
                text += ', '
            text += f'({column}, {str(value)})'
        return text

    # just to make sure columns and data line up
    @staticmethod
    def prepare_to_add_to_master_table(table_name: str, column_dict: dict) -> tuple:
        columns = ('table_name', 'column_data')
        data = (table_name, DB_general.column_data_as_string(column_dict))
        return (columns, data)

    # get info on all the tables in the database
    def get_table_data(self):
        raw_table_data = self.select_columns(DB_general.master_table_name, [col[0] for col in DB_general.master_table_columns])
        table_data = None
        if raw_table_data is not None:
            table_data = dict()
            for line in raw_table_data:
                table_data[line[0]] = DB_general.string_to_column_data(line[1])
        return table_data
    
    # initialize just by giving the location of the database, and maybe table_data as a dict
    def __init__(self, filepath_of_db) -> None:
        self.filepath = filepath_of_db
        self.tables = self.get_table_data()
        # make sure master table exists
        if self.tables is None:
            self.tables = dict()
            self.create_table(DB_general.master_table_name, DB_general.master_table_columns_dict)
            # self.tables = {DB_general.master_table_name: DB_general.master_table_columns_dict}
        

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
        # check if table already exists
        check_name = self.select_rows_by_column_value(DB_general.master_table_name, DB_general.master_table_column_names[0], table_name)
        # print(f'chack_name is {check_name}')
        if check_name is None or check_name == []:
            success = True
            conn = self.connect()[0]
            with conn:
                command = create_table_command(table_name, column_data)
                try:
                    conn.execute(command)
                    self.tables[table_name] = column_data
                    print('Table', table_name, 'created')
                except sqlite3.OperationalError:
                    # I guess there could be other errors, but...
                    success = False
                    print('Table', table_name, 'already exists, but its not in', DB_general.master_table_name)
                if check_name is None:
                    command = create_table_command(DB_general.master_table_name, DB_general.master_table_columns_dict)
                    try:
                        conn.execute(command)
                    except sqlite3.OperationalError:
                        # table does not exist by check_name, but somehow we got an error
                        print('problems with', DB_general.master_table_name)
            conn.close()
            if success:
                columns_and_data = DB_general.prepare_to_add_to_master_table(table_name, column_data)
                self.insert(DB_general.master_table_name, *columns_and_data)
                
        else:
            print('Table', table_name, 'already exists')
            print(check_name[0], 'should be the same as', table_name)
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
            try:
                conn.execute(command, data)
            except sqlite3.IntegrityError as error:
                print('Unable to insert:', error)
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
                cur.execute(f'SELECT rowid, * FROM {table_name}')
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
            command = f'SELECT rowid, * FROM {table_name} WHERE {column} = ?;'
            # command = 'SELECT rowid, * FROM ' + table_name + ' WHERE ' + column + ' = ?;'
            try:
                cur.execute(command, (value,))
                rows = cur.fetchall()
            except sqlite3.OperationalError:
                # presumably table does not exist
                rows = None
        return rows

    def select_rows_by_text_wo_capitalization(self, table_name, column, text):
        conn, cur = self.connect()
        with conn:
            command = f'SELECT rowid, * FROM {table_name} WHERE {column} LIKE ?;'
            # command = 'SELECT rowid, * FROM ' + table_name + ' WHERE ' + column + ' LIKE ?;'
            cur.execute(command, (text,))
            rows = cur.fetchall()
        return rows
    
    # get info on row with specific rowid
    def select_row_by_rowid(self, table_name, rowid):
        rows = self.select_rows_by_column_value(table_name, 'rowid', rowid)
        return rows[0]

    # backup db to another file
    def backup_db(self, new_filename):
        backup_db = DB_general(new_filename)
        everything = self.get_table_data()
        for table, col_data in everything.items():
            if table != DB_general.master_table_name:
                backup_db.create_table(table, col_data)
                rows_in_table = self.select_columns(table, col_data.keys())
                if rows_in_table is not None:
                    for row in rows_in_table:
                        backup_db.insert(table, col_data.keys(), row)

