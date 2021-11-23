from pathlib import Path
import sqlite3
import pytest

import fix_imports
from db import DB
# import db_ini

# DB with no data perhaps
@pytest.fixture
def db0():
    yield DB(testing=True)
    # delete the file?
    # Path('test_rct_data.db').unlink()

# and then a copy of the whole thing
@pytest.fixture
def db():
    return DB(is_backup_db=True)


def test_table_name_for_EIN_ratings():
    assert DB.table_name_for_EIN_ratings('3D Cinema') == 'Cinema'
    assert DB.table_name_for_EIN_ratings('Lay Down Roller Coaster') == 'LayDownRollerCoaster'
    assert DB.table_name_for_EIN_ratings('Merry Go Round') == 'MerryGoRound'


def test_ride_row_as_dict():
    ride_row = (37, 'Giga Coaster', 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', 707, 559, 297)
    ride = DB.ride_row_as_dict(ride_row)
    assert ride['rowid'] == 37
    assert ride['name'] == 'Giga Coaster'
    assert ride['rideBonusValue'] == 120
    assert ride['excitementValue'] == 51
    assert ride['EIN_table_name'] == 'GigaCoaster'
    assert ride['defaultExcitement'] > 600

def test_age_mod_row_as_dict():
    age_row = (0, 5, 3, 2, 0)
    age_mod = DB.age_mod_row_as_dict(age_row)
    assert age_mod == {'from': 0, 'to': 5, 'multiplier': 3, 'divisor': 2, 'addition': 0}
    age_row = (200, None, 81, 1024, 0)
    age_mod = DB.age_mod_row_as_dict(age_row)
    assert age_mod == {'from': 200, 'to': '', 'multiplier': 81, 'divisor': 1024, 'addition': 0}

def test_init():
    test_folder = Path(__file__).resolve().parent
    db1 = DB(is_backup_db=True)
    assert db1.filepath == test_folder.parent / 'rct_data_backup.db'
    db2 = DB()
    assert db2.filepath == test_folder.parent / 'rct_data.db'
    # test db should have
    db3 = DB(testing=True)
    assert db3.filepath.parent == test_folder
    assert db3.filepath == test_folder / 'test_rct_data.db'
    assert DB.ride_table_name in db3.tables
    assert DB.alias_table_name in db3.tables
    assert DB.age_table_name in db3.tables
    assert DB.age_table_name_classic in db3.tables
    # remove the db file??
    Path(test_folder / 'test_rct_data.db').unlink()


def test_create_table_for_ride_ratings(db0):
    ride = 'Merry Go Round'
    db0.create_table_for_ride_ratings(ride)
    columns = ('excitement', 'intensity', 'nausea')
    db0.insert('MerryGoRound', columns, (100, 60, 75))
    rows = db0.select_all('MerryGoRound')
    assert rows[0] == (1, 100, 60, 75, None)
    # remove the table
    db0.drop_table('MerryGoRound')
    assert 'MerryGoRound' not in db0.get_table_data()


# using 'full' data
def test_get_ride_names(db):
    ride_names = db.get_ride_names(False)
    assert len(ride_names) == 79
    assert 'Giga Coaster' in ride_names
    assert 'Swinging Ship' in ride_names
    assert 'Pirate Ship' not in ride_names

    ride_names = db.get_ride_names()
    # hopefully alias table is not empty
    if aliases := db.select_all(db.alias_table_name):
        print('yeah there is stuff in aliases')
        assert len(ride_names) == 79 + len(aliases)
        assert 'Pirate Ship' in ride_names
        assert 'Water Slide' in ride_names

def test_get_age_ranges(db):
    age_ranges = db.get_age_ranges()
    assert len(age_ranges) == 10
    assert age_ranges[0] == {'from': 0, 'to': 5}
    assert age_ranges[2] == {'from': 13, 'to': 40}
    assert age_ranges[6] == {'from': 104, 'to': 120}
    assert age_ranges[-1] == {'from': 200, 'to': ''}

def test_get_age_modifiers(db):
    # assert DB.age_table_name in db.get_table_data()
    # assert set(('age_start', 'age_end', 'multiplier', 'divisor', 'addition')) == set(db.get_table_data()[DB.age_table_name].keys())
    age_mod = db.get_age_modifiers()
    assert len(age_mod['new']) == 10
    assert len(age_mod['old']) == 10
    assert age_mod['new'][0] == {'from': 0, 'to': 5, 'multiplier': 3, 'divisor': 2, 'addition': 0}
    assert age_mod['old'][0] == {'from': 0, 'to': 5, 'multiplier': 1, 'divisor': 1, 'addition': 30}
    assert age_mod['new'][9] == {'from': 200, 'to': '', 'multiplier': 9, 'divisor': 16, 'addition': 0}
    assert age_mod['old'][-1] == {'from': 200, 'to': '', 'multiplier': 9, 'divisor': 16, 'addition': 0}

def test_find_ride_info(db):
    ride_info = db.find_ride_info('Giga Coaster')
    assert ride_info['name'] == 'Giga Coaster'
    assert ride_info['rideBonusValue'] == 120
    assert ride_info['excitementValue'] == 51
    assert ride_info['nauseaValue'] == 10

    ride_info = db.find_ride_info('Monorail')
    assert ride_info['name'] == 'Monorail'
    assert ride_info['rideBonusValue'] == 60
    assert ride_info['excitementValue'] == 70
    assert ride_info['nauseaValue'] == -10
    assert ride_info['visible_name'] == 'Monorail'


def test_find_og_name_of_ride(db):
    names = ['pirate ship', 'Giga coaster', 'Water Slide']
    og_names = ['Swinging Ship', 'Giga Coaster', 'Dinghy Slide']
    for name, og_name in zip(names, og_names):
        assert db.find_og_name_of_ride(name) == og_name

def test_get_ride_rowid(db):
    ride_name = 'Haunted House'
    rowid = db.get_ride_rowid(ride_name)
    
    row = db.select_row_by_rowid(DB.ride_table_name, rowid)
    assert ride_name in row

def test_get_EIN_table_name_for_ride(db):
    ride = '3d Cinema'
    assert db.get_EIN_table_name_for_ride(ride) == DB.table_name_for_EIN_ratings(ride)
    ride = 'Log Flume'
    assert db.get_EIN_table_name_for_ride(ride) == DB.table_name_for_EIN_ratings(ride)
    ride = 'Pirate Ship'
    assert db.get_EIN_table_name_for_ride(ride) == 'SwingingShip'

def test_get_EIN_values_for_ride(db):
    ride = 'Giga Coaster'
    EIN_values = db.get_EIN_values_for_ride(ride)
    assert EIN_values == (51, 32, 10)


# back to modifying db
def test_add_ride(db0):
    # make sure there is nothing in rides
    assert db0.select_all(DB.ride_table_name) == []

    ride_data = ('Giga Coaster', 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', 700, 500, 300)
    db0.add_ride(ride_data)
    assert db0.select_all(DB.ride_table_name)[0][1:] == ride_data

    # remove the row
    conn, cur = db0.connect()
    with conn:
        cur.execute(f'DELETE FROM {DB.ride_table_name} WHERE name = ?;', ('Giga Coaster',))
    conn.close()
    assert db0.select_all(DB.ride_table_name) == []


def test_get_default_EIN_for_ride(db0):
    ride = 'Giga Coaster'
    row = (ride, 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', 700, 500, 300)
    db0.add_ride(row)
    default_EIN = db0.get_default_EIN_for_ride(ride)
    assert default_EIN[0] == 700
    assert default_EIN[1] == 500
    assert default_EIN[2] == 300
    # remove the row
    conn, cur = db0.connect()
    with conn:
        cur.execute(f'DELETE FROM {DB.ride_table_name} WHERE name = ?;', (ride,))
    conn.close()
    assert db0.select_all(DB.ride_table_name) == []

def test_add_alias(db0):
    # make sure there is nothing in rides and aliases
    assert db0.select_all(DB.ride_table_name) == []
    assert db0.select_all(DB.alias_table_name) == []
    # add giga coaster
    og_names = ('Giga Coaster', 'Super Coaster', 'Imaginary Coaster')
    # ride_data = (og_name, 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', 700, 500, 300)
    for og_name in og_names:
        ride_data = (og_name, 120, 51, 32, 10, DB.table_name_for_EIN_ratings(og_name), og_name, None, None, None)
        db0.add_ride(ride_data)
    # make an alias for giga coaster
    aliases = ('Gigantic Coaster', 'Superior Coaster', 'Nonexistent Coaster')
    db0.add_alias(aliases[0], og_names[0], is_visible=False, EIN_modifiers=(10, 15, 10))
    db0.add_alias(aliases[1], og_names[1], is_visible=True, EIN_modifiers=None)
    db0.add_alias(aliases[2], og_names[2], is_visible=False, EIN_modifiers=(-5, -10, -100))
    # check alias table
    alias_content = db0.select_all(DB.alias_table_name)
    assert alias_content[0] == (1, aliases[0], 1, og_names[0], 0, 10, 15, 10)
    assert alias_content[1] == (2, aliases[1], 2, og_names[1], 1, None, None, None)
    assert alias_content[2] == (3, aliases[2], 3, og_names[2], 0, -5, -10, -100)    

    # remove the rows
    og_names = [(og_name,) for og_name in og_names]
    aliases = [(alias,) for alias in aliases]
    conn, cur = db0.connect()
    with conn:
        cur.executemany(f'DELETE FROM {DB.ride_table_name} WHERE name = ?;', og_names)
        cur.executemany(f'DELETE FROM {DB.alias_table_name} WHERE name = ?;', aliases)
    conn.close()
    assert db0.select_all(DB.ride_table_name) == []
    assert db0.select_all(DB.alias_table_name) == []
    

def test_insert_values_for_ride_ratings(db0):
    pass

def test_update_default_values(db0):
    pass

def test_calculate_average_EIN(db0):
    pass

def test_set_average_values_as_default(db0):
    pass

def test_set_average_values_as_default_for_all(db0):
    pass



def test_calculate_max_prices(db0):
    pass