from pathlib import Path
import sqlite3
import pytest

import fix_imports
from db import DB

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


def test_init():
    test_folder = Path(__file__).resolve().parent
    db1 = DB(is_backup_db=True)
    assert db1.filepath == test_folder.parent / 'rct_data_backup.db'
    db2 = DB()
    assert db2.filepath == test_folder.parent / 'rct_data.db'
    db3 = DB(testing=True)
    assert db3.filepath.parent == test_folder
    assert db3.filepath == test_folder / 'test_rct_data.db'


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
