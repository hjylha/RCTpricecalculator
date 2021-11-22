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

