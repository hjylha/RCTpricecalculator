from statistics import mean
import time

from db_stuff import DB_general
from db_ini import get_columns_for_table, get_db_path, get_column_names_for_table
from calc import calc_max_prices


# more specific database class
class DB(DB_general):
    ride_table_name = 'rides'
    age_table_name = 'age_modifiers'
    age_table_name_classic = 'age_modifiers_classic'
    alias_table_name = 'aliases'
    EIN_table_name = 'individual_ride_tables'

    @staticmethod
    def table_name_for_EIN_ratings(ride_name) -> str:
        if ride_name.lower() == '3d cinema':
            return 'Cinema'
        return ''.join(ride_name.split(' '))

    @staticmethod
    def ride_row_as_dict(row) -> dict:
        columns = ['rowid'] + list(get_column_names_for_table(DB.ride_table_name))
        return {column: item for item, column in zip(row, columns)}
        # return {'name': row[1], 
        #         'excitementValue': row[3],
        #         'intensityValue': row[4],
        #         'nauseaValue': row[5],
        #         'EIN_table_name': row[6],
        #         'visible_name': row[7],
        #         'defaultExcitement': row[8],
        #         'defaultIntensity': row[9],
        #         'defaultNausea': row[10],
        #         'rideBonusValue': row[2],
        #         'rowid': row[0]}
    
    # is this needed?
    @staticmethod
    def age_mod_row_as_dict(row) -> dict:
        columns = get_column_names_for_table(DB.age_table_name)
        age_mod0 = DB.table_row_as_dict(row, columns)
        age_mod = {key: age_mod0[key] for key in columns[2:]}
        # make sure None changes to empty string
        def none_as_empty_string(item):
            if item is None:
                return ''
            return item
        age_mod['from'] = age_mod0['age_start']
        age_mod['to'] = none_as_empty_string(age_mod0['age_end'])
        return age_mod

    def __init__(self, is_backup_db=False, existing=True, testing=False) -> None:
        # test db does not need to exist
        if testing:
            # filepath = get_db_path(testing=True)[0]
            super().__init__(get_db_path(testing=True)[0])
        # if we are 'connecting' to backup db, it should exist
        elif is_backup_db:
            super().__init__(get_db_path()[-1])
        # 'connect' to an existing db
        elif existing:
            super().__init__(get_db_path()[0])
        # strictly speaking, finally db can exist or not
        else:
            super().__init__(get_db_path(False)[0])
            # self.generate_rides(True)
            # self.generate_age_modifiers()
            # self.create_table(DB.alias_table_name, get_columns_for_table(DB.alias_table_name))
        # make sure the main tables exist
        table_names = (DB.ride_table_name, DB.age_table_name, DB.age_table_name_classic, DB.alias_table_name)
        for table in table_names:
            if table not in self.tables:
                self.create_table(table, get_columns_for_table(table))
        
    # create a table for EIN ratings of a ride
    def create_table_for_ride_ratings(self, ride_name) -> None:
        table_name = DB.table_name_for_EIN_ratings(ride_name)
        columns = get_columns_for_table(DB.EIN_table_name)
        self.create_table(table_name, columns)
    
    # get names of all rides in db, includes aliases by default
    # TODO: use visible names instead
    def get_ride_names(self, with_aliases=True) -> list:
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

    # get age ranges as a list of {'from': age_start, 'to': age_end}
    def get_age_ranges(self) -> list:
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

    # get all the age modifiers
    def get_age_modifiers(self):
        age_modifiers = dict()
        # openrct2 modifiers
        columns = get_column_names_for_table(DB.age_table_name)
        age_modifiers0 = self.select_columns(DB.age_table_name, columns)
        age_modifiers['new'] = [DB.age_mod_row_as_dict(age) for age in age_modifiers0]
        # classic modifiers
        age_modifiers1 = self.select_columns(DB.age_table_name_classic, columns)
        age_modifiers['old'] = [DB.age_mod_row_as_dict(age) for age in age_modifiers1]
        return age_modifiers

    # search for a ride by name, ignoring capitalization
    def find_ride_info(self, ride_name):
        rides = self.select_rows_by_text_wo_capitalization(DB.ride_table_name, 'name', ride_name)
        if rides:
            return DB.ride_row_as_dict(rides[0])
        # maybe ride_name is alias
        rides = self.select_rows_by_text_wo_capitalization(DB.alias_table_name, 'name', ride_name)
        if rides:
            OG_rowid = rides[0][2]
            ride_row = self.select_row_by_rowid(DB.ride_table_name, OG_rowid)
            if ride_row:
                return DB.ride_row_as_dict(ride_row)

    # find the og name of ride
    def find_og_name_of_ride(self, ride_name):
        return self.find_ride_info(ride_name)['name']

    # just get the rowid of the row containing ride
    def get_ride_rowid(self, ride_name):
        ride_info = self.find_ride_info(ride_name)
        return ride_info['rowid']

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

    # add a new ride to the ride table (probably useless fcn)
    def add_ride(self, ride_data):
        columns = get_column_names_for_table(DB.ride_table_name)
        self.insert(DB.ride_table_name, columns, ride_data)    
    
    # add alias
    def add_alias(self, alias, og_ride, is_visible=True, EIN_modifiers=None):
        ride_info = self.find_ride_info(og_ride)
        columns = get_column_names_for_table(DB.alias_table_name)
        alias_data = [alias, ride_info['rowid'], ride_info['name']]
        # alias_data = [capitalize_first_letters(alias), ride_info['rowid'], ride_info['name']]
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

    # insert ride ratings to db
    def insert_values_for_ride_ratings(self, ride_name, EIN, with_timestamp=True):
        # make sure aliases point to the og ride name
        # og_ride = self.find_og_name_of_ride(ride_name)
        table_name = self.get_EIN_table_name_for_ride(ride_name)
        columns = get_column_names_for_table(DB.EIN_table_name)
        if with_timestamp:
            data = tuple(list(EIN) + [int(time.time())])
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

    # create a csv file containing data in main tables
    def write_main_tables_to_csv_file(self, filename):
        main_tables =  [DB.ride_table_name, DB.alias_table_name, DB.age_table_name, DB.age_table_name_classic]
        for table in main_tables:
            with open(filename, 'a') as f:
                f.write(f'\n[{table}]\n')
            self.create_csv_file(table, filename)

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
    
    # finally, just print a lot of stuff
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
