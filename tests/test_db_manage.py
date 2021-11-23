from pathlib import Path
import pytest

import fix_imports
import db_manage
from db_manage import DB

# 'empty' db
@pytest.fixture
def db():
    yield db_manage.DB(testing=True)
    # remove db after use?
    path = Path(__file__).parent / 'test_rct_data.db'
    path.unlink()

# 'empty' db with all tables
@pytest.fixture
def dbe(db):
    db_manage.generate_rides(db)
    db_manage.generate_age_modifiers(db)
    return db

# 'full' db
@pytest.fixture
def db0():
    return db_manage.DB(is_backup_db=True)


def test_generate_rides(db):
    db_manage.generate_rides(db, False)
    rides = db.select_all(DB.ride_table_name)
    assert len(rides) == 79
    assert 'Go Karts' in [ride[1] for ride in rides]
    assert DB.table_name_for_EIN_ratings('Go Karts') not in db.tables

def test_generate_rides_and_ein_tables(db):
    db_manage.generate_rides(db)
    rides = db.select_all(DB.ride_table_name)
    assert len(rides) == 79
    names = [ride[1] for ride in rides]
    assert 'Go Karts' in names
    for name in names:
        assert db.select_all(DB.table_name_for_EIN_ratings(name)) is not None


def test_generate_age_modifiers(db):
    # make sure there is nothing in the age modifiers table
    assert db.select_all(DB.age_table_name) == []
    db_manage.generate_age_modifiers(db)
    age_mod = db.get_age_modifiers()
    assert age_mod['new'][0] == {'from': 0, 'to': 5, 'multiplier': 3, 'divisor': 2, 'addition': 0}
    assert age_mod['old'][0] == {'from': 0, 'to': 5, 'multiplier': 1, 'divisor': 1, 'addition': 30}
    assert age_mod['new'][9] == {'from': 200, 'to': '', 'multiplier': 9, 'divisor': 16, 'addition': 0}

def test_check_aliases(db):
    pass

def test_import_ratings_from_old_db(db):
    pass

def test_import_aliases_from_old_db(db):
    pass

def test_generate_clean_db(db):
    pass

def test_generate_db_using_backup(db):
    pass