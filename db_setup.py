from db_stuff import DB_general
from db_ini import get_columns_for_table, get_db_path, get_column_names_for_table
from get_data import get_age_modifiers_from_file, get_ride_data_from_files
from get_data import check_missing_for_alias, capitalize_first_letters
from calc import calc_max_prices
# from get_data import read_age_values  # probably should get rid of this
# from pathlib import Path
from statistics import mean
import time

# db_filename = 'rct_data.db'
# ride_table_name = "rides"
# age_table_name = "age_modifiers"

# create dict with columns for rides' attributes
# def create_rides_columns():
#     return {'name': ('TEXT', 'NOT NULL', 'UNIQUE'), 
#         'rideBonusValue': ('INTEGER', 'NOT NULL'),
#         'excitementValue': ('INTEGER', 'NOT NULL'),
#         'intensityValue': ('INTEGER', 'NOT NULL'),
#         'nauseaValue': ('INTEGER', 'NOT NULL'),
#         'alias_of': ("INTEGER",),
#         'defaultExcitement': ('INTEGER',),
#         'defaultIntensity': ('INTEGER',),
#         'defaultNausea': ('INTEGER',)}


# # create dict with columns for age modifiers
# def create_age_columns():
#     return {'age_start': ('INTEGER', 'NOT NULL', 'UNIQUE'),
#         'age_end': ('INTEGER', 'UNIQUE'),
#         'modifier_type': ('TEXT', 'NOT NULL'),
#         'modifier': ('INTEGER', 'NOT NULL'),
#         'modifier_type_classic': ('TEXT', 'NOT NULL'),
#         'modifier_classic': ('INTEGER', 'NOT NULL')}

# # create dict with columns for EIN modifiers
# def create_EIN_columns():
#     return {'excitement': ('INTEGER', 'NOT NULL'),
#             'intensity': ('INTEGER', 'NOT NULL'),
#             'nausea': ('INTEGER', 'NOT NULL')}

# # create dict with columns for default EIN values
# def create_default_EIN_columns():
#     return {'defaultExcitement': ('INTEGER',),
#             'defaultIntensity': ('INTEGER',),
#             'defaultNausea': ('INTEGER',)}

# # create dict with columns of alias table
# def create_alias_table_columns():
#     return{'name': ('TEXT', 'NOT NULL', 'UNIQUE'),
#             'OG_rowid': ('INTEGER', 'NOT NULL'),
#             'OG_name': ('TEXT', 'NOT NULL')}

# # table name for table storing EIN ratings of a ride w rowid 37 is 'ein37'
# # or well, it used to be
# def table_for_EIN_ratings(rowid):
#     return 'ein' + str(rowid)

# old table data
# def create_table_data_old():
#     table_data = dict()
#     table_data[ride_table_name] = create_rides_columns()
#     table_data[age_table_name] = create_age_columns()
#     for i in range(1,80):
#         table_name = table_for_EIN_ratings(i)
#         table_data[table_name] = create_EIN_columns()
#     return table_data





# more specific database class
class DB(DB_general):
    # db_filename = 'rct_data.db'
    # db_filename = get_db_path()[0]
    # backup_db_filename = 'rct_data_backup.db'
    # backup_db_filename = get_db_path()[-1]
    ride_table_name = 'rides'
    age_table_name = 'age_modifiers'
    age_table_name_classic = 'age_modifiers_classic'
    alias_table_name = 'aliases'
    EIN_table_name = 'individual_ride_tables'

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
                'visible_name': row[7],
                'defaultExcitement': row[8],
                'defaultIntensity': row[9],
                'defaultNausea': row[10],
                'rideBonusValue': row[2],
                'ride_id': row[0]}

    def __init__(self, is_backup_db=False, existing=True) -> None:
        # if we are 'connecting' to backup db, it should exist
        if is_backup_db:
            if filepath := get_db_path()[-1]:
                super().__init__(filepath)
            else:
                print('no database with given path found')
        # 'connect' to an existing db
        elif existing:
            super().__init__(get_db_path()[0])
        # strictly speaking, finally db can exist or not
        else:
            super().__init__(get_db_path(False)[0])
            self.generate_rides(True)
            self.generate_age_modifiers()
            self.create_table(DB.alias_table_name, get_columns_for_table(DB.alias_table_name))
            
            
        # if w_full_table_data:
        #     ride_names0 = self.select_columns(DB.ride_table_name, ('name',))
        #     ride_names = [DB.table_name_for_EIN_ratings(ride[0]) for ride in ride_names0]
        #     for ride in ride_names:
        #         self.tables[ride] = create_EIN_columns()
        #     # add more tables to master table
        #     for table in self.tables:
        #         columns_and_data = DB.prepare_to_add_to_master_table(table, self.tables[table])
        #         self.insert(DB.master_table_name, *columns_and_data)
        

    def create_table_for_ride_ratings(self, ride_name):
        table_name = DB.table_name_for_EIN_ratings(ride_name)
        columns = get_columns_for_table(DB.EIN_table_name)
        self.create_table(table_name, columns)
    
    # check openrct files and get info about rides from there
    def generate_rides(self, with_EIN_tables=False):
        # create rides table
        column_data = get_columns_for_table(DB.ride_table_name)
        self.create_table(DB.ride_table_name, column_data)

        # get ride data
        rides = get_ride_data_from_files()

        # insert ride data to rides table
        # columns = (name, bonusvalue, EV, IV, NV, EIN_table_name, visible_name)
        columns = get_column_names_for_table(DB.ride_table_name)[:7]
        # columns = ('name', 'rideBonusValue', 'excitementValue', 'intensityValue', 'nauseaValue', 'EIN_table_name', 'visible_name')
        for ride in rides:
            EIN, bonusvalue = rides[ride]
            EIN_table_name = DB.table_name_for_EIN_ratings(ride)
            data = (ride, bonusvalue, EIN[0], EIN[1], EIN[2], EIN_table_name, ride)
            self.insert(DB.ride_table_name, columns, data)

        # create rating tables for each ride
        if with_EIN_tables:
            for ride in rides:
                self.create_table_for_ride_ratings(ride)
                # print(ride, 'has EIN table', DB.table_name_for_EIN_ratings(ride))       

    # get age modifiers from openrct2 files
    def generate_age_modifiers(self):
        # create age modifier tables
        column_data = get_columns_for_table(DB.age_table_name)
        self.create_table(DB.age_table_name, column_data)
        self.create_table(DB.age_table_name_classic, column_data)

        # get age modifiers
        age_modifiers = get_age_modifiers_from_file()

        # insert modifiers to age table
        columns = get_column_names_for_table(DB.age_table_name)
        start_age = 0
        for line in age_modifiers['new']:
            # print('line in age modifiers:', line)
            if start_age != line[0]:
                data = (start_age, *line)
            else:
                data = (start_age, None, *line[1:])
            start_age = line[0]
            self.insert(DB.age_table_name, columns, data)
        # and the same for classic modifiers
        start_age = 0
        for line in age_modifiers['old']:
            if start_age != line[0]:
                data = (start_age, *line)
            else:
                data = (start_age, None, *line[1:])
            start_age = line[0]
            self.insert(DB.age_table_name_classic, columns, data)
        
        # get age modifiers from csv files
        # age_columns = create_age_columns()
        # self.create_table(DB.age_table_name, age_columns)
        # age_values = read_age_values()
        # for age in age_values:
        #     data = [age[column] for column in list(age_columns.keys())[2:]]
        #     if age['to'] != '':
        #         data.insert(0, age['to'])
        #     else:
        #         data.insert(0, None)
        #     data.insert(0, age['from'])
        #     self.insert(DB.age_table_name, age_columns, data)

    # get names of all rides in db, includes aliases by default
    def get_ride_names(self, with_aliases=True):
        # names0 = self.select_columns(DB.ride_table_name, ('visible_name',))
        names0 = self.select_columns(DB.ride_table_name, ('name',))
        names = [name[0] for name in names0]
        if with_aliases:
            names1 = self.select_columns(DB.alias_table_name, ('name',))
            if names1 is not None:
                names1 = [name[0] for name in names1]
                names = names + names1
        names.sort()
        return names

    def get_age_ranges(self):
        age_ranges = []
        age_ranges0 = self.select_columns(DB.age_table_name, get_column_names_for_table(DB.age_table_name)[:2])
        for ages in age_ranges0:
            age = {'from': ages[0]}
            if ages[1] is not None:
                age['to']= ages[1]
            else:
                age['to'] = ''
            age_ranges.append(age)
        return age_ranges

    def get_age_modifiers(self):
        age_modifiers = dict()
        # openrct2 modifiers
        age_modifiers['new'] = []
        age_modifiers0 = self.select_all(DB.age_table_name)
        for age in age_modifiers0:
            age_modifier = {'from': age[1]}
            if age[2] is not None:
                age_modifier['to'] = age[2]
            else:
                age_modifier['to'] = ''
            age_modifier['multiplier'] = age[3]
            age_modifier['divisor'] = age[4]
            age_modifier['addition'] = age[5]
            age_modifiers['new'].append(age_modifier)
        # classic modifiers
        age_modifiers['old'] = []
        age_modifiers1 = self.select_all(DB.age_table_name_classic)
        for age in age_modifiers1:
            age_modifier = {'from': age[1]}
            if age[2] is not None:
                age_modifier['to'] = age[2]
            else:
                age_modifier['to'] = ''
            age_modifier['multiplier'] = age[3]
            age_modifier['divisor'] = age[4]
            age_modifier['addition'] = age[5]
            age_modifiers['old'].append(age_modifier)
        return age_modifiers

    # search for a ride by name, ignoring capitalization
    def find_ride_info(self, ride_name):
        rides = self.select_rows_by_text_wo_capitalization(DB.ride_table_name, 'name', ride_name)
        if len(rides) > 0:
            return DB.ride_row_as_dict(rides[0])
        # maybe ride_name is alias
        rides = self.select_rows_by_text_wo_capitalization(DB.alias_table_name, 'name', ride_name)
        if len(rides) > 0:
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

    # IS THIS A DUPLICATE??? table_name_for_EIN_ratings(ride_name)
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
    # TODO maybe update these things
    def check_aliases(self):
        aliases = check_missing_for_alias(self.get_ride_names(False))
        columns = get_column_names_for_table(DB.alias_table_name)
        for og_ride, alias in aliases:
            data = (alias, self.get_ride_rowid(og_ride), og_ride)
            self.insert(DB.alias_table_name, columns, data)
    
    # insert ride ratings to db
    def insert_values_for_ride_ratings(self, ride_name, EIN, with_timestamp=True):
        # make sure aliases point to the og ride name
        # og_ride = self.find_og_name_of_ride(ride_name)
        table_name = self.get_EIN_table_name_for_ride(ride_name)
        columns = get_column_names_for_table(DB.EIN_table_name)
        if with_timestamp:
            data = tuple(list(EIN) + int(time.time()))
            self.insert(table_name, columns, data)
        else:
            self.insert(table_name, columns[:3], EIN)

    # set new default/average values for EIN
    def update_default_values(self, ride_name, new_default_EIN):
        rowid = self.get_ride_rowid(ride_name)
        EIN_columns = get_column_names_for_table(DB.ride_table_name)[-3:]
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
    def add_alias(self, alias, og_ride, is_visible=True, EIN_modifiers=None):
        ride_info = self.find_ride_info(og_ride)
        columns = get_column_names_for_table(DB.alias_table_name)
        alias_data = [capitalize_first_letters(alias), ride_info['ride_id'], ride_info['name']]
        # visibility of the name
        if is_visible:
            alias_data += [1]
        else:
            alias_data += [0]
        # if alias has EIN modifiers, put them in the end, otherwise ignore those columns
        if EIN_modifiers is not None:
            alias_data += list(EIN_modifiers)
        else:
            columns = columns[:-3]
        self.insert(DB.alias_table_name, columns, alias_data)

    # import EIN ratings for rides from old style db
    def import_ratings_from_old_db(self, old_db):
        old_ride_data = old_db.select_all(DB.ride_table_name)
        for ride in old_ride_data:
            # try to find the matching ride in the new ride table
            ride_info = self.find_ride_info(ride[1])
            if ride_info is not None:
                old_EIN_table = DB.table_name_for_EIN_ratings(ride[1])
                old_EIN_data = old_db.select_all(old_EIN_table)
                # make sure there is something in EIN table for this ride
                if old_EIN_data is not None:
                    ride_name = ride_info['name']
                    for data in old_EIN_data:
                        self.insert_values_for_ride_ratings(ride_name, data[1:], False)
    
    # import aliases from old db
    def import_aliases_from_old_db(self, old_db):
        cols = list(old_db.get_table_data()[DB.alias_table_name].keys())
        
        old_aliases = old_db.select_columns(DB.alias_table_name, cols)
        if 'is_visible' not in cols:
            add_to_line = True
            cols += ['is_visible']
        for line in old_aliases:
            if add_to_line:
                line = list(line) + [1]
            self.insert(DB.alias_table_name, cols, line)
    
    def generate_clean_db(self):
        # create basic tables
        self.create_table(DB.ride_table_name, get_columns_for_table(DB.ride_table_name))
        print('created table', DB.ride_table_name)
        # self.create_table(DB.age_table_name, create_age_columns())
        self.create_table(DB.alias_table_name, get_columns_for_table(DB.alias_table_name))
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
        # init hopefully creates some stuff
        # self.check_aliases()
        # print('aliases checked')
        self.import_aliases_from_old_db(DB(is_backup_db=True))
        print('aliases imported')
        self.import_ratings_from_old_db(DB(is_backup_db=True))
        print('ratings imported')
        self.set_average_values_as_default_for_all()
        print('averages set as default EIN values')

    # create a csv file containing data in main tables
    def write_main_tables_to_csv_file(self, filename):
        main_tables =  [DB.ride_table_name, DB.alias_table_name, DB.age_table_name, DB.age_table_name_classic]
        for table in main_tables:
            with open(filename, 'a') as f:
                f.write(f'\n[{table}]\n')
            self.create_csv_file(table, filename)

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
        columns = get_column_names_for_table(DB.ride_table_name)
        self.insert_data(DB.ride_table_name, columns, ride_data)

    # calculate max price table for a ride
    def calculate_max_prices(self, ride : str, EIN : tuple, free_entry : bool) -> list:
        age_modifiers = self.get_age_modifiers()
        EIN_modifiers = self.get_EIN_values_for_ride(ride)
        max_prices = []
        for age_modifier in age_modifiers['new']:
            prices = calc_max_prices(EIN, EIN_modifiers, age_modifier, free_entry)
            max_prices.append(prices)
        for i, age_modifier in enumerate(age_modifiers['old']):
            prices = calc_max_prices(EIN, EIN_modifiers, age_modifier, free_entry)
            max_prices[i] = (*max_prices[i], *prices)
        return max_prices
