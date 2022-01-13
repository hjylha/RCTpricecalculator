from pathlib import Path
import sqlite3
import pytest

import fix_imports
import db as dbf
from db import DB
# import db_ini

# DB with no data perhaps
@pytest.fixture
def db0():
    yield DB(testing=True)
    # delete the file?
    # Path('test_rct_data.db').unlink()

# add some rides and EIN tables for those rides (or just one...)
@pytest.fixture
def db1(db0):
    ride = ('Giga Coaster', 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', None, None, None)
    db0.add_ride(ride)
    db0.create_table_for_ride_ratings(ride[0])
    yield db0
    # remove EIN table and inserted ride
    db0.drop_table(DB.table_name_for_EIN_ratings(ride[0]))
    conn, cur = db0.connect()
    with conn:
        cur.execute(f'DELETE from {DB.ride_table_name} WHERE name = ?;', (ride[0],))
    conn.close()

# add some EIN ratings for giga coaster
@pytest.fixture
def db2(db1):
    ride = 'Giga Coaster'
    EIN_values = [(700, 500, 300), (650, 450, 275), (675, 475, 250)]
    for ein in EIN_values:
        db1.insert_values_for_ride_ratings(ride, ein, False)
    return db1

# and then a copy of the whole thing
@pytest.fixture
def db():
    return DB(is_backup_db=True)


@pytest.mark.parametrize(
    'ride_name, table_name', [
        ('3D Cinema', 'Cinema'),
        ('Lay Down Roller Coaster', 'LayDownRollerCoaster'),
        ('Merry Go Round', 'MerryGoRound')
    ]
)
def test_table_name_for_EIN_ratings(ride_name, table_name):
    assert DB.table_name_for_EIN_ratings(ride_name) == table_name
    # assert DB.table_name_for_EIN_ratings('3D Cinema') == 'Cinema'
    # assert DB.table_name_for_EIN_ratings('Lay Down Roller Coaster') == 'LayDownRollerCoaster'
    # assert DB.table_name_for_EIN_ratings('Merry Go Round') == 'MerryGoRound'


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


# get ride names and visible names once and then check what it contains
@pytest.fixture
def names(db):
    return db.get_ride_names_and_visible_names()

@pytest.mark.parametrize(
    'ride_name, visible_name', [
        ('Giga Coaster',  'Giga Coaster'),
        ('Merry Go Round', 'Merry-Go-Round'),
        ('Water Slide', 'Dinghy Slide'),
        ('Roto-Drop', 'Roto-Drop')
    ]
)
def test_get_ride_names_and_visible_names(names, ride_name, visible_name):
    assert names[ride_name] == visible_name


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


@pytest.mark.parametrize(
    'name, og_name', [
        ('pirate ship', 'Swinging Ship'),
        ('Giga coaster', 'Giga Coaster'),
        ('Water Slide', 'Dinghy Slide')
    ]
)
def test_find_og_name_of_ride(db, name, og_name):
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
    # also the EIN table is created
    assert db0.select_all(DB.table_name_for_EIN_ratings(ride_data[0])) == []

    # remove the row and EIN table
    conn, cur = db0.connect()
    with conn:
        cur.execute(f'DELETE FROM {DB.ride_table_name} WHERE name = ?;', ('Giga Coaster',))
    conn.close()
    assert db0.select_all(DB.ride_table_name) == []
    db0.drop_table(DB.table_name_for_EIN_ratings(ride_data[0]))
    assert db0.select_all(DB.table_name_for_EIN_ratings(ride_data[0])) is None


def test_get_default_EIN_for_ride(db0):
    ride = 'Giga Coaster'
    row = (ride, 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', 700, 500, 300)
    db0.add_ride(row)
    assert db0.get_default_EIN_for_ride(ride) == (700, 500, 300)
    # default_EIN = db0.get_default_EIN_for_ride(ride)
    # assert default_EIN[0] == 700
    # assert default_EIN[1] == 500
    # assert default_EIN[2] == 300
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
    

def test_insert_values_for_ride_ratings(db1):
    # ride_row = ('Giga Coaster', 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', 700, 500, 300)
    ride = 'Giga Coaster'
    EIN_table = DB.table_name_for_EIN_ratings(ride)
    EIN_values = [(700, 500, 300), (650, 450, 275), (675, 475, 250)]
    start_time = int(dbf.time.time())
    for ein in EIN_values:
        db1.insert_values_for_ride_ratings(ride, ein)
    end_time = int(dbf.time.time())
    # timestamp should be unique, so all of these cannot be inserted
    EIN_ratings = db1.select_all(EIN_table)
    # assuming of course that t
    assert end_time - start_time <= 1
    assert len(EIN_ratings) < 3
    assert EIN_ratings[0][:4] == (1, 700, 500, 300)
    # technically time could increment to the next second
    assert EIN_ratings[0][-1] in (start_time, end_time)

    # remove ratings and insert them again without timestamp
    conn, cur = db1.connect()
    with conn:
        cur.execute(f'DELETE FROM {EIN_table}')
    conn.close()
    for ein in EIN_values:
        db1.insert_values_for_ride_ratings(ride, ein, False)
    EIN_ratings = db1.select_all(EIN_table)
    assert len(EIN_ratings) == 3
    assert EIN_ratings[0] == (1, 700, 500, 300, None)

def test_update_visible_name(db1):
    ride = 'Giga Coaster'
    new_name = 'Testing-Stuff With Update'
    db1.update_visible_name(ride, new_name)
    selection = db1.select_columns(DB.ride_table_name, ('visible_name',))
    assert selection[0][0] == new_name

def test_update_default_values(db1):
    ride = 'Giga Coaster'
    # there should not be any default values
    assert db1.get_default_EIN_for_ride(ride) == (None, None, None)
    default_EIN = (700, 500, 300)
    db1.update_default_values(ride, default_EIN)
    assert db1.get_default_EIN_for_ride(ride) == default_EIN

def test_update_alias_visibility(db1):
    db1.add_alias('testalias', 'Giga Coaster')
    assert db1.select_columns(DB.alias_table_name, ('is_visible',))[0][0] == 1
    db1.update_alias_visibility('testalias', False)
    assert db1.select_columns(DB.alias_table_name, ('is_visible',))[0][0] == 0

def test_update_EIN_modifiers_of_alias(db1):
    db1.add_alias('testalias', 'Giga Coaster')
    columns = ('excitement_modifier', 'intensity_modifier', 'nausea_modifier')
    assert db1.select_columns(DB.alias_table_name, columns)[0] == (None, None, None)
    new_ein_mod = (10, 5, None)
    db1.update_EIN_modifiers_of_alias('testalias', new_ein_mod)
    assert db1.select_columns(DB.alias_table_name, columns)[0] == new_ein_mod

def test_calculate_average_EIN(db2):
    ride = 'Giga Coaster'
    assert db2.calculate_average_EIN(ride) == (675, 475, 275)

def test_set_average_values_as_default(db2):
    ride = 'Giga Coaster'
    # there should not be any default values
    assert db2.get_default_EIN_for_ride(ride) == (None, None, None)
    # set average as default
    db2.set_average_values_as_default(ride)
    assert db2.get_default_EIN_for_ride(ride) == (675, 475, 275)

def test_set_average_values_as_default_for_all(db2):
    # add ferris wheel and some EIN ratings for it
    ride_row = ('Ferris Wheel', 42, 5, 2, 1, 'FerrisWheel', 'Ferris Wheel', None, None, None)
    db2.add_ride(ride_row)
    db2.create_table_for_ride_ratings(ride_row[0])
    EIN_ratings = [(125, 50, 55), (135, 50, 55), (100, 50, 55)]
    for ein in EIN_ratings:
        db2.insert_values_for_ride_ratings(ride_row[0], ein, False)
    # set average as default for all
    db2.set_average_values_as_default_for_all()
    ride_data = db2.select_all(DB.ride_table_name)
    assert ride_data[0][-3:] == (675, 475, 275)
    assert ride_data[1][-3:] == (120, 50, 55)


@pytest.mark.parametrize(
    'free_entry, index, prices', [
        (True, 0, (1760, 1320, 1780,  1340)),
        (True, 5, (480, 360, 480, 360)),
        (False, 0, (440, 340, 440, 340)),
        (False, 5, (120, 100, 120, 100))
    ]
)
def test_calculate_max_prices(db, free_entry, index, prices):
    ride = 'Giga Coaster'
    EIN = (800, 550, 400)
    # max_prices = db.calculate_max_prices(ride, EIN, True)
    max_prices = db.calculate_max_prices(ride, EIN, free_entry)
    assert max_prices[index] == prices
    # # assert max_prices[0] == (1760, 1320, 1780, 1320)
    # # assert max_prices[0] == (440, 320, 440, 320)
    # # assert max_prices[5] == (120, 80, 120, 80)

# TODO
def test_write_main_tables_to_csv_file(db):
    pass

def test_print_stuff(db):
    # does anyone care about this?
    pass
