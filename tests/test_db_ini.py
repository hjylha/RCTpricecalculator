import fix_imports

import db_ini

# tables = ['rides', 'age_modifiers', 'aliases', 'individual_ride_tables']
# this should be a path in db.ini
path = db_ini.Path('C:\\Ohjelmointiprojekteja\\PythonProjects\\RCTpricecalculator\\rct_data.db')


def test_make_sure_path_is_absolute():
    assert db_ini.make_sure_path_is_absolute(db_ini.Path('rct_data.db')) == path
    assert db_ini.make_sure_path_is_absolute(path) == path

def test_get_db_path():
    db_paths = db_ini.get_db_path(False)
    # path = db_ini.Path('C:\\Ohjelmointiprojekteja\\PythonProjects\\RCTpricecalculator\\rct_data.db')
    assert path in db_paths
    assert path.parent / 'rct_data_backup.db' in db_paths
    # test db
    db_paths = db_ini.get_db_path(False, True)
    assert db_paths == [path.parent / 'tests' / 'test_rct_data.db']
    assert path.parent / 'tests' / 'test_rct_data.db' == db_ini.get_db_path(testing=True)[0]


def test_get_columns_for_table():
    table = 'rides'
    column_data = db_ini.get_columns_for_table(table)
    assert column_data['EIN_table_name'][2] == 'UNIQUE'

    table = 'age_modifiers'
    column_data = db_ini.get_columns_for_table(table)
    assert column_data['multiplier'][0] == 'INTEGER'

    table2 = 'age_modifiers_classic'
    column_data2 = db_ini.get_columns_for_table(table2)
    assert column_data2['multiplier'][0] == 'INTEGER'

    table = 'individual_ride_tables'
    column_data = db_ini.get_columns_for_table(table, False)
    assert column_data[0][0] == 'excitement'


def test_get_column_names_for_table():
    table = 'aliases'
    columns = db_ini.get_column_names_for_table(table)
    assert columns[:3] == ('name', 'OG_rowid', 'OG_name')


def test_get_columns_for_tables():
    tables = ['rides', 'age_modifiers', 'aliases', 'age_modifiers_classic']
    table_data = db_ini.get_columns_for_tables(tables)
    assert 'rideBonusValue' in table_data['rides']
    assert 'NOT NULL' in table_data['age_modifiers']['age_start']
    assert table_data['aliases']['is_visible'] == ('INTEGER', 'NOT NULL') 
    assert table_data['age_modifiers_classic']['age_end'][1] == 'UNIQUE'



def test_get_db_info():

    db_info = db_ini.get_db_info()
    # path = db_ini.Path('C:\\Ohjelmointiprojekteja\\PythonProjects\\RCTpricecalculator\\rct_data.db')
    assert path in db_info['filepaths']
    assert db_info['table_data']['individual_ride_tables']['timestamp'][0] == 'INTEGER'