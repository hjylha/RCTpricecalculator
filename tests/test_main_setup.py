
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


def test_price_color():
    pass


def test_get_EIN_value():
    pass


def test_get_EIN_values():
    pass
