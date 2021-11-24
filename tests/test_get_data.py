import fix_imports

import get_data


# test getting EIN multipliers and ridebonusvalue
class TestGetRideProperties():
    def test_get_ratings_multipliers(self):
        line = 'SET_FIELD(RatingsMultipliers, { 48, 28, 7 }),'
        assert get_data.get_ratings_multipliers(line) == (48, 28, 7)

        line = 'SET_FIELD(BonusValue, 65),'
        assert get_data.get_ratings_multipliers(line) is None

    def test_get_rides_bonusvalue(self):
        line = 'SET_FIELD(RatingsMultipliers, { 48, 28, 7 }),'
        assert get_data.get_rides_bonusvalue(line) is None

        line = 'SET_FIELD(BonusValue, 65),'
        assert get_data.get_rides_bonusvalue(line) == 65

    def test_get_ride_data_from_file(self):
        filepath = get_data.Path('C:\\Ohjelmointiprojekteja\\c++projects\\OpenRCT2\\src\\openrct2\\ride\\coaster\\meta\\GigaCoaster.h')
        with open(filepath, 'r') as f:
            ride_data = get_data.get_ride_data_from_file(f)
        assert ride_data[0] == (51, 32, 10)
        assert ride_data[1] == 120

    def test_add_spaces_to_ride_names(self):
        # name = 'GigaCoaster'
        assert get_data.add_spaces_to_ride_names('GigaCoaster') == 'Giga Coaster'
        assert get_data.add_spaces_to_ride_names('3DCinema') == '3D Cinema'
        assert get_data.add_spaces_to_ride_names('LIMLaunchedRollerCoaster') == 'LIM Launched Roller Coaster'

    def test_get_ride_data_from_files(self):
        rides = get_data.get_ride_data_from_files()
        assert 'Giga Coaster' in rides
        assert rides['Giga Coaster'] == ((51, 32, 10), 120)

        assert 'Merry Go Round' in rides
        assert rides['Merry Go Round'] == ((50, 10, 0), 45)


# test getting age modifiers
class TestGetAgeModifiers():
    def test_get_age_modifiers_from_line(self):
        line = '        { 64, 3, 4, 0 },      // 0.75x'
        assert get_data.get_age_modifiers_from_line(line) == (64, 3, 4, 0)

    def test_get_age_table(self):
        path = get_data.Path('C:\\Ohjelmointiprojekteja\\c++projects\\OpenRCT2\\src\\openrct2\\ride\\RideRatings.cpp')
        with open(path, 'r') as f:
            age_dict = get_data.get_age_table(f)
        assert 'new' in age_dict
        assert 'old' in age_dict
        assert len(age_dict['new']) == 10
        assert age_dict['new'][8][2] == 1024

    def test_get_age_modifiers_from_file(self):
        age_dict = get_data.get_age_modifiers_from_file()
        assert 'new' in age_dict
        assert 'old' in age_dict
        assert len(age_dict['new']) == 10
        assert age_dict['new'][7][2] == 512


# test getting visible names
def test_get_visible_names_from_file():
    # filepath = get_data.Path(__file__).parent.parent / 'data' / 'visible_names.txt'
    # filepath = get_data.Path('data/visible_names.txt')
    names = get_data.get_visible_names_from_file()
    assert 'Gentle Rides' in names
    assert 'Water Rides' in names
    assert 'Lay-down Roller Coaster' in names['Roller Coasters']
    assert 'Roto-Drop' in names['Thrill Rides']
    t_rides = set(('Chairlift', 'Lift', 'Miniature Railway', 'Monorail', 'Suspended Monorail'))
    assert set(names['Transport Rides']) == t_rides

def test_write_visible_names_to_file():
    data_folder = get_data.Path(__file__).parent.parent / 'data'
    # filepath_og = data_folder / 'visible_names.txt'
    # filepath_og = get_data.Path('data/visible_names.txt')
    names = get_data.get_visible_names_from_file()
    # filepath = get_data.Path('data/visible_names_ord_test.txt')
    filepath = data_folder / 'visible_names_ord_test.txt'
    get_data.write_visible_names_to_file(names, filepath)
    names_ord = get_data.get_visible_names_from_file()
    for title, rides in names.items():
        assert set(rides) == set(names_ord[title])
    
    big_index = names_ord['Roller Coasters'].index('Steeplechase')
    smaller_index = names_ord['Roller Coasters'].index('Hypercoaster')
    assert smaller_index < big_index
    filepath.unlink()

def test_get_aliases_from_alias_file():
    # filepath = get_data.Path(__file__).parent.parent / 'data' / 'alias_list.csv'
    aliases = get_data.get_aliases_from_alias_file()
    alias_names = [line[0] for line in aliases]
    assert 'B-Movie Giant Spider Ride' in alias_names
    assert 'Flower Power Ride' in alias_names
    flower_index = alias_names.index('Flower Power Ride')
    assert aliases[flower_index][-4:] == (1, 75, 40, 10)

def test_capitalize_first_letters():
    assert get_data.capitalize_first_letters(123) == 123
    assert get_data.capitalize_first_letters('one job') == 'One Job'
    assert get_data.capitalize_first_letters('lay-down') == 'Lay-Down'
    assert get_data.capitalize_first_letters('b-movie giant spider ride') == 'B-Movie Giant Spider Ride'

def test_capitalize_list():
    test_list = [['merry-go-round', 'merry go round'], ['one job', 'lay-down'], [42]]
    cap_test_list = [['Merry-Go-Round', 'Merry Go Round'], ['One Job', 'Lay-Down'], [42]]
    get_data.capitalize_list(test_list) == cap_test_list

def test_get_numbers_from_text():
    text = 'sldajf23laksjd5lkasdjf7'
    assert get_data.get_numbers_from_text(text) == (23, 5, 7)
    text = 'safd42asdfasdf'
    assert get_data.get_numbers_from_text(text) == (42, None, None)
    text = 'sdfasdfasdg'
    assert get_data.get_numbers_from_text(text) == None

def test_get_aliases_from_missing_rides():
    aliases = get_data.get_aliases_from_missing_rides()
    assert ('Carousel', 'Merry Go Round', None) in aliases
    assert ('Flower Power Ride', 'Flying Saucers', 75, 40, 10) in aliases
    assert ('Haunted Jail House', 'Crooked House', 75, None, None) in aliases
    assert ('Fighting Knights Dodgems', '', None) in aliases

# well this is an interesting test...
# def test_are_missing_rides_in_alias_list():
#     assert get_data.are_missing_rides_in_alias_list()
