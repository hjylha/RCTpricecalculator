import fix_imports

import calc

# more or less following Deurklink's guide
# https://forums.openrct2.org/topic/2737-guide-how-much-can-you-charge-for-your-rides

def test_calculate_ride_value():
    EIN = (800, 550, 400)
    EIN_modifiers = (51, 32, 10)
    assert calc.calculate_ride_value(EIN_modifiers, EIN) == 59


def test_apply_age_to_ride_value():
    age_mod = {'from': 0, 'to': 5, 'multiplier': 3, 'divisor': 2, 'addition': 0}
    assert calc.apply_age_to_ride_value(59, age_mod) == 88
    age_mod2 = {'from': 128, 'to': 200, 'multiplier': 81, 'divisor': 1024, 'addition': 0}
    assert calc.apply_age_to_ride_value(59, age_mod2) == 4


def test_apply_many_rides_modifier():
    assert calc.apply_many_rides_modifier(88) == 66
    assert calc.apply_many_rides_modifier(27) == 20


def test_apply_pay_for_entry():
    assert calc.apply_pay_for_entry(88) == 22
    assert calc.apply_pay_for_entry(27) == 6


def test_maximize_price():
    assert calc.maximize_price(88) == 1760
    assert calc.maximize_price(105) == 2000
    assert calc.maximize_price(4) == 80


def test_calc_max_prices():
    EIN = (800, 550, 400)
    EIN_mod = (51, 32, 10)
    age_mod = {'from': 0, 'to': 5, 'multiplier': 3, 'divisor': 2, 'addition': 0}
    prices = calc.calc_max_prices(EIN, EIN_mod, age_mod, True)
    assert prices == (1760, 1320)


# EIN = (707, 559, 297)
# EIN_modifiers = (51, 32, 10)
# free_entry = True
# age_modifier = {'from': 128, 'to': 200, 'multiplier': 81, 'divisor': 1024, 'addition': 0}

# ride_value = calc.calculate_ride_value(EIN_modifiers, EIN)
# print(ride_value)

# value_after_age = calc.apply_age_to_ride_value(ride_value, age_modifier)
# print(value_after_age)

# value_if_not_unique = calc.apply_many_rides_modifier(value_after_age)
# print(value_if_not_unique)

# value_if_pay_for_entry = calc.apply_pay_for_entry(value_if_not_unique)
# print(value_if_pay_for_entry)

# max_prices = calc.calc_max_prices(EIN, EIN_modifiers, age_modifier, free_entry)
# print(max_prices)