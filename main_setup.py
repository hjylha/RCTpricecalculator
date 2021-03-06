

no_match_text = 'No match found'


# try to find ride names containing given text_input
def get_suggestions_for_ride_name(text_input: str, ride_names: dict, num_of_suggestions: int) -> list:
    suggestions = []
    num = len(text_input)
    # match with start of ride name
    for name, vis_name in ride_names.items():
        if len(suggestions) >= num_of_suggestions:
            return suggestions
            # break
        if name.lower().startswith(text_input.lower()) and vis_name not in suggestions:
            suggestions.append(vis_name)
    # match with any part of ride name
    for name, vis_name in ride_names.items():
        if len(suggestions) >= num_of_suggestions:
            return suggestions
            # break
        if len(name) > num:
            for i in range(1, len(name)- num + 1):
                if name[i:].lower().startswith(text_input.lower()):
                    if vis_name not in suggestions:
                        suggestions.append(vis_name)
    # if nothing found, that is the suggestion
    if not suggestions:
        suggestions.append(no_match_text)
    return suggestions


# if len(word) < num_of_letters, add two spaces for each 'missing' letter
def add_double_spaces(word: str, num_of_letters: int) -> str:
    # if len(word) >= num_of_letters:
    #     return word
    formatted_word = word
    for _ in range(num_of_letters - len(word)):
        formatted_word += '  '
    return formatted_word

# how to show age1 - age2 as a string
def format_age_ranges(age1: int, age2: int) -> str:
    text1 = add_double_spaces(str(age1), 3)
    text2 = add_double_spaces(str(age2), 3)
    return f'{text1}  ...  {text2}'


# divide by 100 and add spaces
def price_as_string(price: int) -> str:
    price_s = str(price)
    if price == 0:
        return '  0.00'
    if price < 100:
        return f'  0.{price_s}'
    if price < 1000:
        return f'  {price_s[0]}.{price_s[1:]}'
    return f'{price_s[:2]}.{price_s[2:]}'


# the better the price, the greener the price
# but mostly just kinda random color decisions
def price_color(price: int) -> tuple:
    # zero price is red
    if price == 0:
        return (1, 0, 0, 1)
    # turn price to a number between 0 and 100
    mult = price // 20
    # high prices are green
    if mult > 49:
        mult = (mult - 50) // 2
        return (0, 0.75 + 0.01*mult, 0, 1)
    # less green, maybe blue
    if mult > 19:
        return (0, 0.4 + 0.01*mult, 0.8 - 0.01*mult, 1)
    # adding some red perhaps
    if mult > 4:
        return (0.4 - 0.01*mult, 0.02 * mult, 0.8 - 0.01*mult, 1)
    # more red for prices under 1 euro/dollar/etc
    mult *= 2
    return (0.9- 0.05*mult, 0, 0.4 + 0.05 * mult, 1)


# turn inputted EIN value into correct form
def get_EIN_value(input_value: str, is_float=False) -> int:
    # if real (float) value is used, multiply it by 100
    if is_float:
        if ',' in input_value:
            comma = input_value.index(",")
            try:
                input_value = f'{input_value[:comma]}.{input_value[comma+1:]}'
            except IndexError:
                input_value = f'{input_value[:-1]}.'
        try:
            return int(float(input_value) * 100)
        except ValueError:
            return 0
    try:
        return int(input_value)
    except ValueError:
        return 0

# EIN_inputs = (e, i, n)
def get_EIN_values(EIN_inputs: tuple) -> tuple:
    # if float values are used
    # if ('.' in EIN_inputs[0] or '.' in EIN_inputs[1] or '.' in EIN_inputs[2]):
    for input in EIN_inputs:
        if ('.' in input or ',' in input) and get_EIN_value(input, True):
            return tuple([get_EIN_value(ein_value, True) for ein_value in EIN_inputs])
    # otherwise, we assume EIN is the real value multiplied by 100
    return tuple([get_EIN_value(ein_value) for ein_value in EIN_inputs])
