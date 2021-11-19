import fix_imports

import get_data


# test getting EIN multipliers and ridebonusvalue
def test_get_ratings_multipliers():
    line = 'SET_FIELD(RatingsMultipliers, { 48, 28, 7 }),'
    assert get_data.get_ratings_multipliers(line) == (48, 28, 7)

    line = 'SET_FIELD(BonusValue, 65),'
    assert get_data.get_ratings_multipliers(line) is None


def test_get_rides_bonusvalue():
    line = 'SET_FIELD(RatingsMultipliers, { 48, 28, 7 }),'
    assert get_data.get_rides_bonusvalue(line) is None

    line = 'SET_FIELD(BonusValue, 65),'
    assert get_data.get_rides_bonusvalue(line) == 65


def test_get_ride_data_from_file():
    filepath = get_data.Path('C:\\Ohjelmointiprojekteja\\c++projects\\OpenRCT2\\src\\openrct2\\ride\\coaster\\meta\\GigaCoaster.h')
    with open(filepath, 'r') as f:
        ride_data = get_data.get_ride_data_from_file(f)
    assert ride_data[0] == (51, 32, 10)
    assert ride_data[1] == 120


def test_add_spaces_to_ride_names():
    # name = 'GigaCoaster'
    assert get_data.add_spaces_to_ride_names('GigaCoaster') == 'Giga Coaster'
    assert get_data.add_spaces_to_ride_names('3DCinema') == '3D Cinema'
    assert get_data.add_spaces_to_ride_names('LIMLaunchedRollerCoaster') == 'LIM Launched Roller Coaster'


def test_get_ride_data_from_files():
    rides = get_data.get_ride_data_from_files()
    assert 'Giga Coaster' in rides
    assert rides['Giga Coaster'] == ((51, 32, 10), 120)

    assert 'Merry Go Round' in rides
    assert rides['Merry Go Round'] == ((50, 10, 0), 45)


# test getting age modifiers
def test_get_age_modifiers_from_line():
    line = '        { 64, 3, 4, 0 },      // 0.75x'
    assert get_data.get_age_modifiers_from_line(line) == (64, 3, 4, 0)


def test_get_age_table():
    path = get_data.Path('C:\\Ohjelmointiprojekteja\\c++projects\\OpenRCT2\\src\\openrct2\\ride\\RideRatings.cpp')
    with open(path, 'r') as f:
        age_dict = get_data.get_age_table(f)
    assert 'new' in age_dict
    assert 'old' in age_dict
    assert len(age_dict['new']) == 10
    assert age_dict['new'][8][2] == 1024


def test_get_age_modifiers_from_file():
    age_dict = get_data.get_age_modifiers_from_file()
    assert 'new' in age_dict
    assert 'old' in age_dict
    assert len(age_dict['new']) == 10
    assert age_dict['new'][7][2] == 512


# test getting visible names
def test_get_visible_names_from_file():
    filepath = get_data.Path('data/visible_names.txt')
    names = get_data.get_visible_names_from_file(filepath)
    assert 'Gentle Rides' in names
    assert 'Water Rides' in names
    assert 'Lay-down Roller Coaster' in names['Roller Coasters']
    assert 'Roto-Drop' in names['Thrill Rides']
    t_rides = set(('Chairlift', 'Lift', 'Miniature Railway', 'Monorail', 'Suspended Monorail'))
    assert set(names['Transport Rides']) == t_rides

    