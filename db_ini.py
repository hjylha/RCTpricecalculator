from pathlib import Path
'''read the file db.ini and extract the info there'''

# print(Path(__file__).resolve().parent)
# path = Path('data/nothing_here.txt')
# print(Path(__file__).resolve().parent.joinpath(path))

# this file (db_ini.py) and db.ini should be in the same directory
ini_file = Path(__file__).resolve().parent / 'db.ini'

# get possible db paths: under [filepath] (by default only get existing file names)
def get_db_path(existing=True):
    paths = []
    with open(ini_file, 'r') as f:
        reading = False
        for line in f:
            # pass empty lines and lines containing #
            if line.strip() == '' or '#' in line:
                pass
            elif reading:
                # if another [ in line, filepath section has ended
                if '[' in line:
                    break
                # otherwise add to possible paths
                path = Path(line.strip())
                # use absolute paths just in case
                if not path.is_absolute():
                    path = Path(__file__).resolve().parent.joinpath(path)
                if (existing and path.exists()) or not existing:
                    paths.append(path)
            # start reading when [filepath] is reached
            elif '[filepath]' in line:
                reading = True
    # print(paths)
    return paths

# get columns for table (as a dict or a tuple)
def get_columns_for_table(table_name, as_dict=True):
    if as_dict:
        columns = dict()
    else:
        columns = []
    with open(ini_file, 'r') as f:
        reading = False
        for line in f:
            # pass empty lines and lines containing #
            if line.strip() == '' or '#' in line:
                pass
            # column_name=(type,stuff1,stuff2)
            elif reading:
                # have we reached the next section?
                if '[' in line:
                    break
                    return columns
                column_name = line.split('=')[0]
                # print(line.split('('))
                data = line.split('(')[1].split(')')[0].split(',')
                info = tuple(item.strip() for item in data)
                if as_dict:
                    columns[column_name] = info
                else:
                    columns.append((column_name, info))
            # [table_name] starts the section to be read
            elif '[' + table_name + ']' in line:
                reading = True
    if not as_dict:
        columns = tuple(columns)
    return columns

# get column info for given tables (as a dict or a tuple)
def get_columns_for_tables(tables, as_dict=True):
    if as_dict:
        table_data = dict()
    else:
        table_data = []
    for table in tables:
        if as_dict:
            table_data[table] = get_columns_for_table(table)
        else:
            table_data.append((table, get_columns_for_table(table, False)))
    if not as_dict:
        table_data = tuple(table_data)
    return table_data

# get everything
def get_db_info():
    db_info = dict()
    db_info['filepaths'] = get_db_path()
    table_names = ['rides', 'age_modifiers', 'aliases', 'individual_ride_tables']
    db_info['table_data'] = get_columns_for_tables(table_names)
    return db_info