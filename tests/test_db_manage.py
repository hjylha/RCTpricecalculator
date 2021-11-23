import pytest

import fix_imports
import db_manage

# 'empty' db
@pytest.fixture
def db():
    yield db_manage.DB(testing=True)
    # remove db after use?

# 'full' db
@pytest.fixture
def db0():
    return db_manage.DB(is_backup_db=True)


def test_generate_rides(db):
    pass

def test_generate_age_modifiers(db):
    pass

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