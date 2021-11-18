
# fcns for using csv files
from get_data import read_ride_values, read_age_values

# little functions for the calculator
def rounding(num):
    return int((num // 10) // 10 * 10)

# EIN multipliers as 3-tuple, EIN as 3-tuple (of integers)
def calculate_ride_value(EIN_multipliers : tuple, EIN : tuple) -> int:
    ride_value = 0
    for i in range(len(EIN)):
        ride_value += (EIN[i] * EIN_multipliers[i]) // 1024
    return ride_value

# apply age modifiers to ride value
def apply_age_to_ride_value(ride_value : int, age_modifiers : dict) -> int:
    multiplier = age_modifiers['multiplier']
    divisor = age_modifiers['divisor']
    add = age_modifiers['addition']
    return (ride_value * multiplier) // divisor + add

# if there are many rides of the same type, value drops to 3/4
def apply_many_rides_modifier(modified_value : int) -> int:
    return 3 * modified_value // 4

# if guests have to pay for entering the park value drops to 1/4
def apply_pay_for_entry(modified_value : int) -> int:
    return modified_value // 4

# maximal price is 2*modified_value/10, or maybe that's the first unacceptable price?
def maximize_price(modified_value : int) -> int:
    # price in cents or whatever (so we are dealing with integers)
    # max_price = 2 * modified_value * 10
    return min(2000, 20 * modified_value)

# calculate max prices in cases of unique ride and many similar rides
def calc_max_prices(EIN : tuple, EIN_multipliers : tuple, age_modifier : dict, free_entry : bool) -> tuple:
    ride_value = calculate_ride_value(EIN_multipliers, EIN)
    # print(ride_value)
    modified_value = apply_age_to_ride_value(ride_value, age_modifier)
    # print(modified_value)
    if not free_entry:
        modified_value = apply_pay_for_entry(modified_value)
    modified_value_nonunique = apply_many_rides_modifier(modified_value)
    return (maximize_price(modified_value), maximize_price(modified_value_nonunique))

# 2*normal_price -10 or just 2*normal_price ?
def maximize(normal_price):
    price = 2 * normal_price - 10
    if price < 0:
        return 0
    if price > 2000:
        return 2000
    return price

# age_value = {'modifier': num, 'modifier_type': char, 'modifier_classic': num, 'modifier_type_classic': char}
def calculate_price_w_age(ride_value, age_value, free_entry):
    if not free_entry:
        # in case of pay-for-entry, prices are quarter of those with free entry
        ride_value = (ride_value // 4)
    multiplier, multiplier_c = age_value['modifier'], age_value['modifier_classic']
    # non-unique prices are three quarters of unique prices
    price_unique = maximize(rounding(ride_value * multiplier))
    price = maximize(rounding((3* ride_value // 4) * multiplier))
    if age_value['modifier_type_classic'] == '*':
        price_unique_c = maximize(rounding(ride_value * multiplier_c))
        price_c = maximize(rounding((3*ride_value // 4) * multiplier_c))
    else:
        price_unique_c = maximize(rounding(100 * (ride_value+multiplier_c)))
        price_c = maximize(rounding(300 * (ride_value+multiplier_c) // 4))
    return (price_unique, price, price_unique_c, price_c)

# calculate_prices based on ride value and age values
def calculate_prices(ride_value, age_values, free_entry):
    max_prices = []
    for age in age_values:
        price_line = calculate_price_w_age(ride_value, age, free_entry)
        max_prices.append(price_line)
    return max_prices


# EIN as integers (i.e. multiplied by 100)
def calculate_price_table(EIN_multipliers, EIN, age_values, free_entry=True):
    ride_value = calculate_ride_value(EIN_multipliers, EIN)
    return calculate_prices(ride_value, age_values, free_entry)


# other way to calculate prices, aimed for the case where ride_values are read from files
def calculate_max_prices(ride_values, age_values, ride_type, excitement, intensity, nausea, free_entry=True):
    if ride_type.lower() in ride_values.keys():
        e_multiplier = ride_values[ride_type]['excitementValue']
        i_multiplier = ride_values[ride_type]['intensityValue']
        n_multiplier = ride_values[ride_type]['nauseaValue']
    else:
        # print('Cannot find ride of type', ride_type)
        # should a new exception class be defined for this?
        raise Exception('Given ride type not found: ' + ride_type)
    # ride_value = (excitement * e_multiplier) // 1024 + (intensity * i_multiplier) // 1024 + (nausea * n_multiplier) // 1024
    ride_value = calculate_ride_value((e_multiplier, i_multiplier, n_multiplier), (excitement, intensity, nausea))
    return calculate_prices(ride_value, age_values, free_entry)

# read data from files and calculate
def calculate_max_price(ride_type, excitement, intensity, nausea, free_entry=True):
    ride_values = read_ride_values()
    age_values = read_age_values()
    return calculate_max_prices(ride_values, age_values, ride_type, excitement, intensity, nausea, free_entry)
    

# trying to make words same length (this is probably not needed)
def add_empty_space_at_the_end(word, length):
    if len(word) < length:
        new_word = word
        for _ in range(length - len(word)):
            new_word = new_word + ' '
        return new_word
    return word


# create the calculator to run in terminal
def calculator():
    ride_name = input('What is the ride type? ')
    print('Type the rating values of the ride without dots, i.e. multiplied by 100.')
    excitement = int(input('Excitement rating of the ride: '))
    intensity = int(input('Intensity rating of the ride: '))
    nausea = int(input('Nausea rating of the ride: '))
    ans = input('Do you also charge for park entry? ')
    if ans.lower() == 'yes' or ans.lower() == 'y':
        free_entry = False
    else:
        free_entry = True
    max_prices = calculate_max_price(ride_name, excitement, intensity, nausea, free_entry)
    print('\nThese are the maximum prices you can charge, depending on the age of the ride.\n')
    print('Age\t', 'Max price (openRCT2)', 'Max price (classic)', sep='\t')
    age_values = read_age_values()
    for i, price_line in enumerate(max_prices):
        from_ = add_empty_space_at_the_end(str(age_values[i]['from']), 3)
        to_ = add_empty_space_at_the_end(str(age_values[i]['to']), 3)
        print(from_ + ' ... ' + to_ + '\t', *price_line, sep='\t')


# if __name__ == '__main__':
#     calculator()
