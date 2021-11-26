
import fix_imports
import main_setup


def test_get_suggestions_for_ride_name():
    names = {'name': 'visible_name',
             'good name': 'visible_name',
             'something else': 'nothing',
             'alternative name': 'alt_name',
             'zzz': 'zzz'}
    num_of_suggestions = 3
    text = ''
    sugg = main_setup.get_suggestions_for_ride_name(text, names, num_of_suggestions)
    assert sugg == ['visible_name', 'nothing', 'alt_name']

    text = 'a'
    sugg = main_setup.get_suggestions_for_ride_name(text, names, num_of_suggestions)
    assert sugg == ['alt_name', 'visible_name']

    text = 'q'
    sugg = main_setup.get_suggestions_for_ride_name(text, names, num_of_suggestions)
    assert sugg == [main_setup.no_match_text]

    text = 'z'
    sugg = main_setup.get_suggestions_for_ride_name(text, names, num_of_suggestions)
    assert sugg == ['zzz']

    text = 'name'
    sugg = main_setup.get_suggestions_for_ride_name(text, names, num_of_suggestions)
    assert sugg == ['visible_name', 'alt_name']

    text = 'me'
    sugg = main_setup.get_suggestions_for_ride_name(text, names, num_of_suggestions)
    assert sugg == ['visible_name', 'nothing', 'alt_name']


def test_add_double_spaces():
    num_of_letters = 5
    text = 'text12'
    assert text == main_setup.add_double_spaces(text, num_of_letters)

    text = 'text1'
    assert text == main_setup.add_double_spaces(text, num_of_letters)

    text = 'text'
    assert 'text  ' == main_setup.add_double_spaces(text, num_of_letters)

    text = 'tex'
    assert 'tex    ' == main_setup.add_double_spaces(text, num_of_letters)


def test_format_age_ranges():
    age1 = 3
    age2 = 10
    assert '3      ...  10  ' == main_setup.format_age_ranges(age1, age2)

    age1 = 13
    age2 = 40
    assert '13    ...  40  ' == main_setup.format_age_ranges(age1, age2)

    age1 = 80
    age2 = 110
    assert '80    ...  110' == main_setup.format_age_ranges(age1, age2)

    age1 = 200
    age2 = ''
    assert '200  ...        ' == main_setup.format_age_ranges(age1, age2)


def test_price_as_string():
    price = 0
    assert '  0.00' == main_setup.price_as_string(price)

    price = 40
    assert '  0.40' == main_setup.price_as_string(price)

    price = 420
    assert '  4.20' == main_setup.price_as_string(price)

    price = 1337
    assert '13.37' == main_setup.price_as_string(price)


# colors are kinda random so...
def test_price_color():
    # price 0 is very red
    price = 0
    assert (1, 0, 0, 1) == main_setup.price_color(price)

    # big prices (>=1000) should be green
    # previous_green = 0.74
    previous_rgb = [0, 0.74, 0]
    for price in range(1000, 2001, 40):
        # price = 40 * i + 1000
        color_tuple = main_setup.price_color(price)
        assert color_tuple[0] == previous_rgb[0]
        assert color_tuple[1] > previous_rgb[1]
        assert color_tuple[1] <= 1
        # previous_rgb[1] = color_tuple[1]
        assert color_tuple[2] == previous_rgb[2]
        previous_rgb = [*color_tuple]
        # transparency or whatever should be 1
        assert color_tuple[-1] == 1
    
    # less green and more blue for prices between 400 and 1000
    # previous_green = 0.59
    # previous_blue = 0.61
    previous_rgb = [0, 0.59, 0.61]
    for price in range(400, 1000, 20):
        # price = 20 * i + 400
        color_tuple = main_setup.price_color(price)
        assert color_tuple[0] == previous_rgb[0]
        assert color_tuple[1] > previous_rgb[1]
        assert color_tuple[1] <= 0.89
        # previous_rgb[1] = color_tuple[1]
        assert color_tuple[2] < previous_rgb[2]
        assert color_tuple[2] >= 0.31
        # previous_rgb[2] = color_tuple[2]
        previous_rgb = [*color_tuple]
        assert color_tuple[-1] == 1
    
    # red comes into play from 100 to 400
    previous_rgb = [0.36, 0.09, 0.76]
    for price in range(100, 400, 20):
        color_tuple = main_setup.price_color(price)
        assert color_tuple[0] < previous_rgb[0]
        assert color_tuple[0] >= 0.2
        assert color_tuple[1] > previous_rgb[1]
        assert color_tuple[1] < 0.4
        assert color_tuple[2] < previous_rgb[2]
        assert color_tuple[2] > 0.6
        previous_rgb = [*color_tuple]
        assert color_tuple[-1] == 1
    
    # under 100
    previous_rgb = [0.91, 0, 0.39]
    for price in range(20, 100, 20):
        color_tuple = main_setup.price_color(price)
        assert color_tuple[0] < previous_rgb[0]
        assert color_tuple[0] > 0.4
        assert color_tuple[1] == previous_rgb[1]
        assert color_tuple[2] > previous_rgb[2]
        assert color_tuple[2] < 0.9
        previous_rgb = [*color_tuple]
        assert color_tuple[-1] == 1


def test_get_EIN_value():
    pass


def test_get_EIN_values():
    pass
