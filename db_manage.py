
from db_ini import get_columns_for_table, get_column_names_for_table
from get_data import get_age_modifiers_from_file, get_ride_data_from_files
from get_data import check_missing_for_alias, capitalize_first_letters
from db import DB

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

# check aliases from missing_rides.txt and add them
# TODO maybe update these things
def check_aliases(self):
    aliases = check_missing_for_alias(self.get_ride_names(False))
    columns = get_column_names_for_table(DB.alias_table_name)
    for og_ride, alias in aliases:
        data = (alias, self.get_ride_rowid(og_ride), og_ride)
        self.insert(DB.alias_table_name, columns, data)


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