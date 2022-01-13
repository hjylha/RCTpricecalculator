from os import name
from pathlib import Path
import pytest

import fix_imports
import get_data
import db_manage
from db_manage import DB

# 'empty' db
@pytest.fixture
def db():
    yield DB(testing=True)
    # remove db after use?
    path = Path(__file__).parent / 'test_rct_data.db'
    path.unlink()

# db with little stuff
@pytest.fixture
def dbs(db):
    ride1 = ('Giga Coaster', 120, 51, 32, 10, 'GigaCoaster', 'Giga Coaster', None, None, None)
    ride2 = ('Merry Go Round', 45, 50, 10, 0, 'MerryGoRound', 'Merry Go Round', 131, 60, 75)
    ride3 = ('Swinging Ship', 35, 50, 30, 10, 'SwingingShip', 'Swinging Ship', 251, 245, 251)
    ride4 = ('Hybrid Coaster', 120, 52, 36, 10, 'HybridCoaster', 'Hybrid Coaster', None, None, None)
    ride5 = ('Corkscrew Roller Coaster', 100, 50, 30, 10, 'CorkscrewRollerCoaster', 'Corkscrew Roller Coaster', 508, 605, 243)
    for ride in (ride1, ride2, ride3, ride4, ride5):
        db.add_ride(ride)
        db.create_table_for_ride_ratings(ride[0])
    return db

# db with all tables and bunch of stuff
@pytest.fixture
def dbe(db):
    if get_data.openrct2_path.exists():
        db_manage.generate_rides(db)
        db_manage.generate_age_modifiers(db)
    else:
        return None
    return db

# 'full' db
@pytest.fixture
def db0():
    return DB(is_backup_db=True)

# real db, probably should not use
# @pytest.fixture
# def db_actual():
#     return DB()

class TestManagement():

    def test_add_aliases_from_alias_list(self, dbe):
        assert dbe is not None
        # alias table should be empty
        assert not dbe.select_all(DB.alias_table_name)
        db_manage.add_aliases_from_alias_list(dbe)
        aliases = dbe.select_all(DB.alias_table_name)
        assert len(aliases) > 50
        # little bit specific to this point in time, but...
        assert (2, 'Carousel', 49, 'Merry Go Round', 0, None, None, None) in aliases

    # maybe a better test is needed here...
    def test_aliases_not_in_alias_list(self, dbs):
        dbs.add_alias('nonsense', 'Giga Coaster')
        dbs.add_alias('Pirate Ship', 'Swinging Ship')
        assert db_manage.aliases_not_in_alias_list(dbs) == ['nonsense']

    def test_visible_names_not_in_db(self, db0):
        names = db_manage.visible_names_not_in_db(db0)
        assert 'Merry-Go-Round' in names
        assert 'Mini Golf' not in names
        assert 'Lay-down Roller Coaster' in names
        assert 'Multi-Dimension Roller Coaster' in names
        assert 'Roto-Drop' in names

    def test_ride_names_not_in_visible_names(self, db0):
        names = db_manage.ride_names_not_in_visible_names(db0)
        print(names)
        assert len(names) == 11
        assert 'Merry Go Round' in names
        assert 'Mini Golf' not in names
        assert 'Lay Down Roller Coaster' in names
        assert 'Multi Dimension Roller Coaster' in names
        assert 'Go Karts' in names
        assert 'Roto Drop' in names

    # not really a proper test, but anyway...
    def test_are_visible_names_accounted_for(self, db0):
        assert db_manage.are_visible_names_accounted_for(db0)

    def test_update_visible_names(self, dbs):
        visible_names = [item[0] for item in dbs.select_columns(DB.ride_table_name, ('visible_name',))]
        assert 'Merry-Go-Round' not in visible_names
        left_out = set(db_manage.update_visible_names(dbs))
        # assert len(left_out) == 1
        assert left_out == {'Hybrid Coaster', 'Swinging Ship'}
        visible_names = [item[0] for item in dbs.select_columns(DB.ride_table_name, ('visible_name',))]
        assert 'Merry-Go-Round' in visible_names
    
    def test_update_alias_info(self, dbs):
        dbs.add_alias('Corkscrew Coaster', 'Corkscrew Roller Coaster', True)
        dbs.add_alias('Double Deck Carousel', 'Merry Go Round', False)
        dbs.add_alias('Pirate Ship', 'Swinging Ship', False)
        db_manage.update_alias_info(dbs)
        columns =('name', 'is_visible', 'excitement_modifier', 'intensity_modifier', 'nausea_modifier')
        selection = dbs.select_columns(DB.alias_table_name, columns)
        corkscrew = [line for line in selection if 'Corkscrew Coaster' in line][0]
        assert corkscrew[1] == 0
        carousel = [line for line in selection if 'Double Deck Carousel' in line][0]
        assert carousel[1] == 1
        assert carousel[-3:] == (11, 3, 1)
        ship = [line for line in selection if 'Pirate Ship' in line][0]
        assert ship[1] == 1
        


class TestGeneration():

    def test_generate_rides(self, db):
        assert get_data.openrct2_path.exists()
        db_manage.generate_rides(db, False)
        rides = db.select_all(DB.ride_table_name)
        assert len(rides) == 79
        assert 'Go Karts' in [ride[1] for ride in rides]
        assert DB.table_name_for_EIN_ratings('Go Karts') not in db.tables

    def test_generate_rides_and_ein_tables(self, db):
        assert get_data.openrct2_path.exists()
        db_manage.generate_rides(db)
        rides = db.select_all(DB.ride_table_name)
        assert len(rides) == 79
        names = [ride[1] for ride in rides]
        assert 'Go Karts' in names
        for name in names:
            assert db.select_all(DB.table_name_for_EIN_ratings(name)) is not None

    def test_generate_age_modifiers(self, db):
        assert get_data.openrct2_path.exists()
        # make sure there is nothing in the age modifiers table
        assert db.select_all(DB.age_table_name) == []
        db_manage.generate_age_modifiers(db)
        age_mod = db.get_age_modifiers()
        assert age_mod['new'][0] == {'from': 0, 'to': 5, 'multiplier': 3, 'divisor': 2, 'addition': 0}
        assert age_mod['old'][0] == {'from': 0, 'to': 5, 'multiplier': 1, 'divisor': 1, 'addition': 30}
        assert age_mod['new'][9] == {'from': 200, 'to': '', 'multiplier': 9, 'divisor': 16, 'addition': 0}

    def test_import_ratings_from_old_db(self, dbe, db0):
        assert dbe is not None
        db_manage.import_ratings_from_old_db(dbe, db0)
        EIN_tables = [line[0] for line in dbe.select_columns(DB.ride_table_name, ('EIN_table_name',))]
        for table in EIN_tables:
            old_ratings = [line[1:] for line in db0.select_all(table)]
            ratings = [line[1:] for line in dbe.select_all(table)]
            if old_ratings and not ratings:
                print(table, 'has no copied ratings')
            for rating in old_ratings:
                assert rating in ratings

    def test_import_aliases_from_old_db(self, db, db0):
        db_manage.import_aliases_from_old_db(db, db0)
        old_aliases = [line[1:] for line in db0.select_all(DB.alias_table_name)]
        aliases = [line [1:] for line in db.select_all(DB.alias_table_name)]
        for alias in old_aliases:
            assert alias in aliases

    def test_generate_clean_db(self, db):
        assert get_data.openrct2_path.exists()
        db_manage.generate_clean_db(db)
        rides = db.select_all(DB.ride_table_name)
        assert len(rides) == 79
        assert len(db.select_all(DB.age_table_name)) == 10
        assert len(db.select_all(DB.age_table_name_classic)) == 10
        for ride in rides:
            assert db.select_all(DB.table_name_for_EIN_ratings(ride[1])) == []

    def test_generate_db_using_backup(self, db):
        db_manage.generate_db_using_backup(db)
        rides = db.select_all(DB.ride_table_name)
        assert len(rides) == 79
        count_none_defaults = 0
        count_no_ein_ratings = 0
        for ride in rides:
            if ride[-1] is None:
                count_none_defaults += 1
            if not db.select_all(DB.table_name_for_EIN_ratings(ride[1])):
                count_no_ein_ratings += 1
        assert count_none_defaults == 2
        assert count_no_ein_ratings == 2
        assert len(db.select_all(DB.age_table_name)) == 10
        assert len(db.select_all(DB.age_table_name_classic)) == 10
        assert len(db.select_all(DB.alias_table_name)) > 0
    