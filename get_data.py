from pathlib import Path

'''functions to get ride values and age modifiers from openrct2 source'''
openrct2_path = Path('C:\\Ohjelmointiprojekteja\\c++projects\\OpenRCT2')

# get data
# from openRCT2 source
# ..\OpenRCT2\src\openrct2\ride
# ride data
# subfolders with .h files:
# coaster\meta
# gentle\meta
# shops\meta   (probably not needed)
# thrill\meta
# transport\meta
# water\meta
# in files RideName.h:
# EIN multipliers:
# SET_FIELD(RatingsMultipliers, { 48, 28, 7 }),
# RideBonusValue:
# SET_FIELD(BonusValue, 65),

# age modifiers:
# RideRatings.cpp
# static const row ageTableNew[] = {
# };
# static const row ageTableOld[] = {
# };

# get ratings multipliers from a line of text, if they are there
def get_ratings_multipliers(line_of_text):
    if 'RatingsMultipliers' in line_of_text:
        numbers = '1234567890'
        start_index = None
        for i, char in enumerate(line_of_text):
            if char in numbers:
                if start_index is None:
                    start_index = i
                end_index = i
        EIN = line_of_text[start_index:end_index + 1].split(',')
        for i, value in enumerate(EIN):
            EIN[i] = int(value.strip())
        return tuple(EIN)
    return None

# get bonusvalue of a ride from a line of text, if it is there
def get_rides_bonusvalue(line_of_text):
    if 'BonusValue' in line_of_text:
        numbers = '1234567890'
        start_index = None
        for i, char in enumerate(line_of_text):
            if char in numbers:
                if start_index is None:
                    start_index = i
                end_index = i
        return int(line_of_text[start_index:end_index+1])
    return None

# get ratings modifiers and bonusvalue from file
def get_ride_data_from_file(file):
    EIN, bonusvalue = None, None
    for line in file:
        if EIN is None:
            EIN = get_ratings_multipliers(line)
        if bonusvalue is None:
            bonusvalue = get_rides_bonusvalue(line)
        if EIN is not None and bonusvalue is not None:
            return (EIN, bonusvalue)

# changing AirPoweredVerticalCoaster into Air Powered Vertical Coaster
def add_spaces_to_ride_names(ride_wo_spaces):
    ride_name = ride_wo_spaces
    i = 1
    while True:
        try:
            char, char_next = ride_name[i], ride_name[i + 1]
            if char.isupper() and char_next.islower():
                ride_name = ride_name[:i] + ' ' + ride_name[i:]
                i += 1
            i += 1
        except IndexError:
            return ride_name

# get EIN modifiers and bonusvalue for all rides with files (except shops)
def get_ride_data_from_files(openrct_path=openrct2_path):
    rides = dict()
    # ..\OpenRCT2\src\openrct2\ride
    ride_path = openrct_path / 'src' / 'openrct2' / 'ride'
    # skip 'shops' folder for now
    folders = ['coaster', 'gentle', 'thrill', 'transport', 'water']
    for folder in folders:
        curr_path = ride_path / folder / 'meta'
        # print(curr_path)
        # get data from ride_name.h files
        files = curr_path.glob('*.h')
        for file in files:
            # print(file)
            ride_name = add_spaces_to_ride_names(file.stem)
            with open(file) as f:
                ride_data = get_ride_data_from_file(f)
            rides[ride_name] = ride_data
    return rides

# get age modifiers from line
def get_age_modifiers_from_line(line):
    values0 = line.split('}')[0].split('{')[1].split(',')
    return tuple([int(value.strip()) for value in values0])

# get age modifiers from a file
# static const row ageTableNew[] = {
# };
# static const row ageTableOld[] = {
# };
def get_age_table(file):
    reading, new_table_done = False, False
    new_table = []
    old_table = []
    for line in file:
        if reading:
            if '};' in line:
                reading = False
                if new_table_done:
                    break
                else:
                    new_table_done = True
            else:
                if new_table_done:
                    old_table.append(get_age_modifiers_from_line(line))
                else:
                    new_table.append(get_age_modifiers_from_line(line))
        else:
            if 'ageTableNew[]' in line:
                reading = True
            elif 'ageTableOld[]' in line:
                reading = True
    return {'new': new_table, 'old': old_table}

# get age modifiers from RideRatings.cpp
def get_age_modifiers_from_file(openrct_path=openrct2_path):
    # age_modifiers = dict()
    file_path = openrct_path / 'src' / 'openrct2' / 'ride' / 'RideRatings.cpp'
    with open(file_path, 'r') as f:
        age_modifiers = get_age_table(f)
        # age_modifiers['old'] = get_age_table(f, False)
    return age_modifiers


'''functions to get aliases from a file'''
# TODO

# here is the old way

# get two rides from a line of text "ride1,ride2,_"
def rides_from_text(line_of_text):
    rides = line_of_text.split(',')
    # ? or ! means ignore that line
    if '?' in rides[1]:
        return ('', '')
    if len(rides) > 2:
        if '!' in rides[2] or '?' in rides[2]:
            return ('', '')
    return (rides[0].strip(), rides[1].strip())

def capitalize_first_letters(text):
    if text == '':
        return text
    text = text[0].upper() + text[1:]
    l = len(text)
    for i in range(1, l):
        if text[i - 1] in ' -':
            try:
                text = text[:i] + text[i].upper() + text[i + 1:]
            except IndexError:
                text = text[:i] + text[i].upper()
    return text

def capitalize_list(list_of_lists):
    new_list = []
    for list_of_text in list_of_lists:
        new_list.append(capitalize_first_letters(text) for text in list_of_text)
    return new_list

# check missing_rides.txt for aliases
def check_missing_for_alias(ride_list):
    aliases = []
    ride_list_l = [ride.lower() for ride in ride_list]
    with open('missing_rides.txt', 'r') as f:
        for line in f:
            ride1, ride2 = rides_from_text(line)
            if ride1.lower() in ride_list_l:
                aliases.append((ride1, ride2))
            elif ride2.lower() in ride_list_l:
                aliases.append((ride2, ride1))
    # list of (og_ride, alias)
    return capitalize_list(aliases)


'''script to read ride values and age modifiers from downloaded file'''

# source = 'C:\Pelit\Useful ride info RCT2.csv'
def read_ride_values(filepath='C:\\Pelit\\Useful ride info RCT2.csv'):
    data = []
    with open(filepath, 'r') as file:
        for line in file:
            list_of_things = line.split(',')
            try:
                int(list_of_things[1])
                item = dict()
                item['ride type'] = list_of_things[0]
                item['rideBonusValue'] = int(list_of_things[1])
                item['excitementValue'] = int(list_of_things[2])
                item['intensityValue'] = int(list_of_things[3])
                item['nauseaValue'] = int(list_of_things[4])
                data.append(item)
            except ValueError:
                pass
    return data

def write_ride_values_to_file(ride_values, filepath='ride_values.csv'):
    with open(filepath, 'w') as file:
        for ride in ride_values:
            line0 = (str(ride['ride type']), 
                str(ride['excitementValue']),
                str(ride['intensityValue']),
                str(ride['nauseaValue']),
                str(ride['rideBonusValue']))
            line = ','.join(line0) + ';\n'
            file.write(line)

def read_age_values(in_classic=False, filepath='C:\\Pelit\\Useful ride info RCT2.csv'):
    data = []
    with open(filepath, 'r') as file:
        index = None
        reading = False
        found = False
        for line in file:
            list_of_things = line.split('\n')[0]
            if '\n' in list_of_things:
                print('onkelma')
            list_of_things = line.split(',')
            if reading and found:
                if list_of_things[index] == '':
                    reading = False
                else:
                    try:
                        second = list_of_things[index + 1]
                        if '+' in second:
                            item = (list_of_things[index], int(second), '+')
                            data.append(item)
                        else:
                            try:
                                other_item = float(second)
                                item = (list_of_things[index], other_item, '*')
                                data.append(item)
                            except ValueError:
                                pass
                    except IndexError:
                        print('jokin on vialla indeksien kanssa')
            else:
                for i, cell in enumerate(list_of_things):
                    if 'Age values' in cell and not found:
                        index = i
                        reading = True
                        if not in_classic:
                            found = True
                        else:
                            in_classic = False
    return data

def get_range(range_as_string):
    items = range_as_string.split(' ')
    if len(items) > 1:
        try:
            return (int(items[0]), int(items[-1]))
        except ValueError:
            pass
    else:
        if '+' in items[0]:
            try:
                return (int(items[0][:-1]), '')
            except ValueError:
                pass

def clean_age_values(age_values):
    new_age_values = []
    # remove the header line (probably not necessary)
    # age_values = age_values[1:]
    for line in age_values:
        try:
            lower_bound, upper_bound = get_range(line[0])
            new_line = (str(lower_bound), str(upper_bound), str(line[1]), str(line[2]))
            new_age_values.append(new_line)
        except TypeError:
            pass
    return new_age_values


def write_age_values_to_file(age_values, in_classic=False):
    filename0 = 'age_modifiers'
    if in_classic:
        filename = filename0 + '_classic.csv'
    else:
        filename = filename0 + '.csv'
    with open(filename, 'w') as file:
        for info in age_values:
            line = ','.join(info) + ';\n'
            file.write(line)

# get ride and age values and write them to file
def main():
    # save ride values to file nearby
    # ride_values = read_ride_values()
    # write_ride_values_to_file(ride_values)
    # save age values to file nearby
    age_values = read_age_values()
    age_values = clean_age_values(age_values)
    write_age_values_to_file(age_values)
    # save classic age values to file nearby
    classic_age_values = read_age_values(in_classic=True)
    classic_age_values = clean_age_values(classic_age_values)
    write_age_values_to_file(classic_age_values, in_classic=True)
    


# read data from files
def read_ride_values():
    ride_values = dict()
    with open('ride_values.csv', 'r') as file:
        for line in file:
            dataline0 = line.split(';')[0]
            dataline = dataline0.split(',')
            # name in lowercase just in case
            name = dataline[0].lower()
            ride_values[name] = dict()
            ride_values[name]['excitementValue'] = int(dataline[1])
            ride_values[name]['intensityValue'] = int(dataline[2])
            ride_values[name]['nauseaValue'] = int(dataline[3])
            ride_values[name]['rideBonusValue'] = int(dataline[4])
    return ride_values

# just consider integers
def read_age_values():
    age_values = []
    with open('age_modifiers.csv', 'r') as file:
        for line in file:
            dataline0 = line.split(';')[0]
            if dataline0 == '':
                break
            dataline = dataline0.split(',')
            age_value = {'from': int(dataline[0])}
            try:
                age_value['to'] = int(dataline[1])
            except ValueError:
                age_value['to'] = ''
            age_value['modifier_type'] = dataline[3]
            age_value['modifier'] = int(100 * float(dataline[2]))
            age_values.append(age_value)
    with open('age_modifiers_classic.csv', 'r') as file:
        for i, line in enumerate(file):
            dataline0 = line.split(';')[0]
            if dataline0 == '':
                break
            dataline = dataline0.split(',')
            age_values[i]['modifier_type_classic'] = dataline[3]
            if dataline[3] == '*':
                age_values[i]['modifier_classic'] = int(100* float(dataline[2]))
            else:
                age_values[i]['modifier_classic'] = int(dataline[2])
    return age_values



        

# no need to do anything here
# if __name__ == '__main__':
#     main()