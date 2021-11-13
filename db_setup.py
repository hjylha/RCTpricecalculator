from db_stuff import DB_general
from get_data import read_age_values  # probably should get rid of this
from pathlib import Path
from statistics import mean

# db_filename = 'rct_data.db'
# ride_table_name = "rides"
# age_table_name = "age_modifiers"

# create dict with columns for rides' attributes
def create_rides_columns():
    return {'name': ('TEXT', 'NOT NULL', 'UNIQUE'), 
        'rideBonusValue': ('INTEGER', 'NOT NULL'),
        'excitementValue': ('INTEGER', 'NOT NULL'),
        'intensityValue': ('INTEGER', 'NOT NULL'),
        'nauseaValue': ('INTEGER', 'NOT NULL'),
        'alias_of': ("INTEGER",),
        'defaultExcitement': ('INTEGER',),
        'defaultIntensity': ('INTEGER',),
        'defaultNausea': ('INTEGER',)}


# create dict with columns for age modifiers
def create_age_columns():
    return {'age_start': ('INTEGER', 'NOT NULL', 'UNIQUE'),
        'age_end': ('INTEGER', 'UNIQUE'),
        'modifier_type': ('TEXT', 'NOT NULL'),
        'modifier': ('INTEGER', 'NOT NULL'),
        'modifier_type_classic': ('TEXT', 'NOT NULL'),
        'modifier_classic': ('INTEGER', 'NOT NULL')}

# create dict with columns for EIN modifiers
def create_EIN_columns():
    return {'excitement': ('INTEGER', 'NOT NULL'),
            'intensity': ('INTEGER', 'NOT NULL'),
            'nausea': ('INTEGER', 'NOT NULL')}

# create dict with columns for default EIN values
def create_default_EIN_columns():
    return {'defaultExcitement': ('INTEGER',),
            'defaultIntensity': ('INTEGER',),
            'defaultNausea': ('INTEGER',)}

# create dict with columns of alias table
def create_alias_table_columns():
    return{'name': ('TEXT', 'NOT NULL', 'UNIQUE'),
            'OG_rowid': ('INTEGER', 'NOT NULL'),
            'OG_name': ('TEXT', 'NOT NULL')}

# table name for table storing EIN ratings of a ride w rowid 37 is 'ein37'
# or well, it used to be
def table_for_EIN_ratings(rowid):
    return 'ein' + str(rowid)

# old table data
# def create_table_data_old():
#     table_data = dict()
#     table_data[ride_table_name] = create_rides_columns()
#     table_data[age_table_name] = create_age_columns()
#     for i in range(1,80):
#         table_name = table_for_EIN_ratings(i)
#         table_data[table_name] = create_EIN_columns()
#     return table_data


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
def get_ride_data_from_files(openrct_path):
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
def get_age_modifiers_from_file(openrct_path):
    # age_modifiers = dict()
    file_path = openrct_path / 'src' / 'openrct2' / 'ride' / 'RideRatings.cpp'
    with open(file_path, 'r') as f:
        age_modifiers = get_age_table(f)
        # age_modifiers['old'] = get_age_table(f, False)
    return age_modifiers

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


# more specific database class
class DB(DB_general):
    db_filename = 'rct_data.db'
    backup_db_filename = 'rct_data_backup.db'
    ride_table_name = 'rides'
    age_table_name = 'age_modifiers'
    alias_table_name = 'aliases'

    @staticmethod
    def table_name_for_EIN_ratings(ride_name):
        if ride_name.lower() == '3d cinema':
            return 'Cinema'
        return ''.join(ride_name.split(' '))
    
    @staticmethod
    def ride_row_as_dict(row):
        return {'name': row[1], 
                'excitementValue': row[3],
                'intensityValue': row[4],
                'nauseaValue': row[5],
                'EIN_table_name': row[6],
                'defaultExcitement': row[7],
                'defaultIntensity': row[8],
                'defaultNausea': row[9],
                'rideBonusValue': row[2],
                'ride_id': row[0]}

    @classmethod
    def create_rides_columns(cls):
        return {'name': ('TEXT', 'NOT NULL', 'UNIQUE'), 
            'rideBonusValue': ('INTEGER', 'NOT NULL'),
            'excitementValue': ('INTEGER', 'NOT NULL'),
            'intensityValue': ('INTEGER', 'NOT NULL'),
            'nauseaValue': ('INTEGER', 'NOT NULL'),
            'EIN_table_name': ('TEXT', 'NOT NULL', 'UNIQUE'),
            'defaultExcitement': ('INTEGER',),
            'defaultIntensity': ('INTEGER',),
            'defaultNausea': ('INTEGER',)}

    @classmethod
    def create_table_data(cls):
        table_data = dict()
        table_data[DB.ride_table_name] = DB.create_rides_columns()
        table_data[DB.age_table_name] = create_age_columns()
        table_data[DB.alias_table_name] = create_alias_table_columns()
        return table_data

    # def __init__(self, filepath_of_db) -> None:
    #     super().__init__(filepath_of_db)
    #     if w_full_table_data:
    #         ride_names0 = self.select_columns(DB.ride_table_name, ('name',))
    #         ride_names = [DB.table_name_for_EIN_ratings(ride[0]) for ride in ride_names0]
    #         for ride in ride_names:
    #             self.tables[ride] = create_EIN_columns()
    #         # add more tables to master table
    #         for table in self.tables:
    #             columns_and_data = DB.prepare_to_add_to_master_table(table, self.tables[table])
    #             self.insert(DB.master_table_name, *columns_and_data)
        

    def create_table_for_ride_ratings(self, ride_name):
        table_name = DB.table_name_for_EIN_ratings(ride_name)
        columns = create_EIN_columns()
        self.create_table(table_name, columns)
    
    # check openrct files and get info about rides from there
    def generate_rides(self, with_EIN_tables=False):
        with open('openrct_path.txt', 'r') as f:
            openrct_path = Path(f.readline().strip())
        rides = get_ride_data_from_files(openrct_path)
        columns = ('name', 'rideBonusValue', 'excitementValue', 'intensityValue', 'nauseaValue', 'EIN_table_name')
        for ride in rides:
            EIN, bonusvalue = rides[ride]
            EIN_table_name = DB.table_name_for_EIN_ratings(ride)
            data = (ride, bonusvalue, EIN[0], EIN[1], EIN[2], EIN_table_name)
            self.insert(DB.ride_table_name, columns, data)
        # create rating tables for each ride
        if with_EIN_tables:
            for ride in rides:
                self.create_table_for_ride_ratings(ride)
                # print(ride, 'has EIN table', DB.table_name_for_EIN_ratings(ride))       

    # get age modifiers from csv files, at least for now
    def generate_age_modifiers(self):
        age_columns = create_age_columns()
        self.create_table(DB.age_table_name, age_columns)
        age_values = read_age_values()
        for age in age_values:
            data = [age[column] for column in list(age_columns.keys())[2:]]
            if age['to'] != '':
                data.insert(0, age['to'])
            else:
                data.insert(0, None)
            data.insert(0, age['from'])
            self.insert(DB.age_table_name, age_columns, data)

    # get names of all rides in db, includes aliases by default
    def get_ride_names(self, with_aliases=True):
        names0 = self.select_columns(DB.ride_table_name, ('name',))
        names = [name[0] for name in names0]
        if with_aliases:
            names1 = self.select_columns(DB.alias_table_name, ('name',))
            if names1 is not None:
                names1 = [name[0] for name in names1]
                names = names + names1
        names.sort()
        return names

    def get_age_modifiers(self):
        age_modifiers = []
        age_modifiers0 = self.select_all(DB.age_table_name)
        for age in age_modifiers0:
            age_modifier = {'from': age[1]}
            if age[2] is not None:
                age_modifier['to'] = age[2]
            else:
                age_modifier['to'] = ''
            age_modifier['modifier_type'] = age[3]
            age_modifier['modifier'] = age[4]
            age_modifier['modifier_type_classic'] = age[5]
            age_modifier['modifier_classic'] = age[6]
            age_modifiers.append(age_modifier)
        return age_modifiers

    # search for a ride by name, ignoring capitalization
    def find_ride_info(self, ride_name):
        rides = self.select_rows_by_text_wo_capitalization(DB.ride_table_name, 'name', ride_name)
        if len(rides) >0:
            return DB.ride_row_as_dict(rides[0])
        # maybe ride_name is alias
        rides = self.select_rows_by_text_wo_capitalization(DB.alias_table_name, 'name', ride_name)
        if len(rides) >0:
            OG_rowid = rides[0][2]
            ride_row = self.select_row_by_rowid(DB.ride_table_name, OG_rowid)
            if len(ride_row) > 0:
                return DB.ride_row_as_dict(ride_row)

    # find the og name of ride
    def find_og_name_of_ride(self, ride_name):
        return self.find_ride_info(ride_name)['name']

    # just get the rowid of the row containing ride
    def get_ride_rowid(self, ride_name):
        ride_info = self.find_ride_info(ride_name)
        return ride_info['ride_id']

    def get_EIN_table_name_for_ride(self, ride_name):
        ride_info = self.find_ride_info(ride_name)
        return ride_info['EIN_table_name']
    
    # get rating modifiers of a ride
    def get_EIN_values_for_ride(self, ride_name):
        ride_info = self.find_ride_info(ride_name)
        return (ride_info['excitementValue'], ride_info['intensityValue'], ride_info['nauseaValue'])

    # get default ratings of a ride
    def get_default_EIN_for_ride(self, ride_name):
        ride_info = self.find_ride_info(ride_name)
        return (ride_info['defaultExcitement'], ride_info['defaultIntensity'], ride_info['defaultNausea'])

    # check aliases from missing_rides.txt and add them
    def check_aliases(self):
        aliases = check_missing_for_alias(self.get_ride_names(False))
        columns = create_alias_table_columns().keys()
        for og_ride, alias in aliases:
            data = (alias, self.get_ride_rowid(og_ride), og_ride)
            self.insert(DB.alias_table_name, columns, data)
    
    # insert ride ratings to db
    def insert_values_for_ride_ratings(self, ride_name, EIN):
        # make sure aliases point to the og ride name
        # og_ride = self.find_og_name_of_ride(ride_name)
        table_name = self.get_EIN_table_name_for_ride(ride_name)
        columns = create_EIN_columns()
        self.insert_and_create_table_if_needed(table_name, columns, EIN)

    # set new default/average values for EIN
    def update_default_values(self, ride_name, new_default_EIN):
        rowid = self.get_ride_rowid(ride_name)
        EIN_columns = create_default_EIN_columns()
        self.update_by_rowid(DB.ride_table_name, EIN_columns, new_default_EIN, rowid)

    # calculate average EIN ratings
    def calculate_average_EIN(self, ride_name):
        # og_ride = self.find_og_name_of_ride(ride_name)
        table = self.get_EIN_table_name_for_ride(ride_name)
        all_data = self.select_all(table)
        # in case of errors, return nothing
        if all_data is None or all_data == []:
            return (None, None, None)
        e_values, i_values, n_values = [], [], []
        for data in all_data:
            e_values.append(data[1])
            i_values.append(data[2])
            n_values.append(data[3])
        # calculate the mean for each rating
        return (int(mean(e_values)), int(mean(i_values)), int(mean(n_values)))

    # calculate average EIN and set them as default
    def set_average_values_as_default(self, ride_name):
        average_EIN = self.calculate_average_EIN(ride_name)
        if average_EIN is not None:
            self.update_default_values(ride_name, average_EIN)
        else:
            print(ride_name, 'does not have recorded ratings')

    # do averaging for all rides
    def set_average_values_as_default_for_all(self):
        # no need to consider aliases
        ride_names = self.get_ride_names(False)
        for ride in ride_names:
            self.set_average_values_as_default(ride)

    # add alias
    def add_alias(self, alias, og_ride):
        ride_info = self.find_ride_info(og_ride)
        columns = create_alias_table_columns().keys()
        alias_data = (capitalize_first_letters(alias), ride_info['ride_id'], ride_info['name'])
        self.insert(DB.alias_table_name, columns, alias_data)

    # import EIN ratings for rides from old style db
    def import_ratings_from_old_db(self, old_db):
        old_ride_data = old_db.select_all(DB.ride_table_name)
        for ride in old_ride_data:
            # try to find the matching ride in the new ride table
            ride_info = self.find_ride_info(ride[1])
            if ride_info is not None:
                old_EIN_table = table_for_EIN_ratings(ride[0])
                old_EIN_data = old_db.select_all(old_EIN_table)
                # make sure there is something in EIN table for this ride
                if old_EIN_data is not None:
                    ride_name = ride_info['name']
                    for data in old_EIN_data:
                        self.insert_values_for_ride_ratings(ride_name, data[1:])
    
    def generate_clean_db(self):
        # create basic tables
        self.create_table(DB.ride_table_name, DB.create_rides_columns())
        print('created table', DB.ride_table_name)
        # self.create_table(DB.age_table_name, create_age_columns())
        self.create_table(DB.alias_table_name, create_alias_table_columns())
        print('created table', DB.alias_table_name)
        # bring in the data
        self.generate_rides(True)
        print('rides generated')
        print('and hopefully also EIN tables for rides')
        self.generate_age_modifiers()
        print('age modifier table and values done')
        self.check_aliases()
        print('aliases checked')

    def generate_db_using_backup(self):
        # create basic tables
        self.create_table(DB.ride_table_name, DB.create_rides_columns())
        print('created table', DB.ride_table_name)
        # self.create_table(DB.age_table_name, create_age_columns())
        # print('created table', DB.age_table_name)
        self.create_table(DB.alias_table_name, create_alias_table_columns())
        print('created table', DB.alias_table_name)
        # bring in the data
        self.generate_rides(True)
        print('rides generated')
        print('and hopefully also EIN tables for rides')
        self.generate_age_modifiers()
        print('age modifier table and values done')
        self.check_aliases()
        print('aliases checked')
        self.import_ratings_from_old_db(DB_general(DB.backup_db_filename))
        self.set_average_values_as_default_for_all()

    def print_stuff(self):
        rides = self.select_all(DB.ride_table_name)
        ages = self.select_all(DB.age_table_name)
        aliases = self.select_all(DB.alias_table_name)

        print('rides')
        for ride in rides:
            print(ride)
        print('\n\nages')
        for age in ages:
            print(age)
        print('\n\naliases')
        for alias in aliases:
            print(alias)

        ride_names = self.get_ride_names(False)
        for ride in ride_names:
            EIN_table = DB.table_name_for_EIN_ratings(ride)
            stuff = self.select_all(EIN_table)
            if stuff is None:
                print(ride, 'has nothing')
            else:
                print(ride, 'has', len(stuff), 'ratings')

    # add a new ride to the ride table (probably useless fcn)
    def add_ride(self, ride_data):
        columns = DB.create_rides_columns().keys()
        self.insert_data(DB.ride_table_name, columns, ride_data)
