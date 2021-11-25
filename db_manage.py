
from db_ini import get_columns_for_table, get_column_names_for_table
from get_data import get_age_modifiers_from_file, get_ride_data_from_files
# from get_data import check_missing_for_alias, capitalize_first_letters
from get_data import get_aliases_from_alias_file, get_visible_names_from_file
from db import DB


# check aliases from missing_rides.txt and add them
# TODO maybe update these things
# def check_aliases(db):
#     aliases = check_missing_for_alias(db.get_ride_names(False))
#     columns = get_column_names_for_table(DB.alias_table_name)
#     for og_ride, alias in aliases:
#         data = (alias, db.get_ride_rowid(og_ride), og_ride)
#         db.insert(DB.alias_table_name, columns, data)

# add aliases from alias list to db
def add_aliases_from_alias_list(db):
    alias_list = get_aliases_from_alias_file()
    for alias in alias_list:
        db.add_alias(alias[0], alias[1], alias[2], alias[3:])

# see which aliases are not in alias list
def aliases_not_in_alias_list(db):
    missing_aliases = []
    aliases = [line[1] for line in db.select_all(DB.alias_table_name)]
    alias_list = [line[0] for line in get_aliases_from_alias_file()]
    for alias in aliases:
        if alias not in alias_list:
            missing_aliases.append(alias)
    return missing_aliases


# find out what normal ride names are not in visible names (so changes have to be made)
def ride_names_not_in_visible_names(db):
    rides_to_look_at = []
    ride_names = db.get_ride_names(False)
    visible_names = []
    for names in get_visible_names_from_file().values():
        visible_names += names

    for ride in ride_names:
        if ride not in visible_names:
            rides_to_look_at.append(ride)
    return rides_to_look_at

# which visible names are not in db
def visible_names_not_in_db(db):
    missing_names = []
    visible_names = []
    for names in get_visible_names_from_file().values():
        visible_names += names
    ride_names = db.get_ride_names(False)
    for name in visible_names:
        if name not in ride_names:
            missing_names.append(name)
    return missing_names

def are_visible_names_accounted_for(db):
    found_all = True
    missing_names = visible_names_not_in_db(db)
    alias_list = [line[0] for line in get_aliases_from_alias_file()]
    for name in missing_names:
        if not name in alias_list:
            print(name)
            found_all = False
    return found_all


# update visible names for rides
def update_visible_names(db):
    ride_names = ride_names_not_in_visible_names(db)
    not_updated = []
    alias_list = get_aliases_from_alias_file()
    for ride in ride_names:
        for alias in alias_list:
            if ride == alias[1] and alias[2] == 1:
                # ride name and visible name should be similar
                # possible issue: Pirate Ship/Swinging Ship
                if alias[0].startswith(ride[:2]):
                    db.update_visible_name(ride, alias[0])
                    break
        else:
            not_updated.append(ride)
    return not_updated


# update alias info (visibility and EIN modifiers) assuming all aliases are in alias list
def update_alias_info(db):
    # (name, og_name, is_visible, e, i, n)
    alias_list = get_aliases_from_alias_file()
    list_names = [line[0] for line in alias_list]
    columns =('name', 'is_visible', 'excitement_modifier', 'intensity_modifier', 'nausea_modifier')
    aliases = db.select_columns(DB.alias_table_name, columns)
    for alias in aliases:
        a_index = list_names.index(alias[0])
        if (visibility := alias_list[a_index][2]) != alias[1]:
            db.update_alias_visibility(alias[0], bool(visibility))
        if (EIN_mod := alias_list[a_index][-3:]) != (None, None, None):
            if EIN_mod != alias[-3:]:
                db.update_EIN_modifiers_of_alias(alias[0], EIN_mod)
        # if mod := alias_list[a_index][-3] != (None, None, None):
        #     if mod != alias[-3:]:
        #         db.update_EIN_modifiers_of_alias(alias[0], mod)
            


# check openrct files and get info about rides from there
def generate_rides(db, with_EIN_tables=True):
    # create rides table
    column_data = get_columns_for_table(DB.ride_table_name)
    db.create_table(DB.ride_table_name, column_data)

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
        db.insert(DB.ride_table_name, columns, data)

    # create rating tables for each ride
    if with_EIN_tables:
        for ride in rides:
            db.create_table_for_ride_ratings(ride)
            # print(ride, 'has EIN table', DB.table_name_for_EIN_ratings(ride))       

# get age modifiers from openrct2 files
def generate_age_modifiers(db):
    # create age modifier tables
    column_data = get_columns_for_table(DB.age_table_name)
    db.create_table(DB.age_table_name, column_data)
    db.create_table(DB.age_table_name_classic, column_data)

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
        db.insert(DB.age_table_name, columns, data)
    # and the same for classic modifiers
    start_age = 0
    for line in age_modifiers['old']:
        if start_age != line[0]:
            data = (start_age, *line)
        else:
            data = (start_age, None, *line[1:])
        start_age = line[0]
        db.insert(DB.age_table_name_classic, columns, data)
    
    # get age modifiers from csv files
    # age_columns = create_age_columns()
    # db.create_table(DB.age_table_name, age_columns)
    # age_values = read_age_values()
    # for age in age_values:
    #     data = [age[column] for column in list(age_columns.keys())[2:]]
    #     if age['to'] != '':
    #         data.insert(0, age['to'])
    #     else:
    #         data.insert(0, None)
    #     data.insert(0, age['from'])
    #     db.insert(DB.age_table_name, age_columns, data)


# import EIN ratings for rides from old style db
def import_ratings_from_old_db(db, old_db):
    old_ride_data = old_db.select_all(DB.ride_table_name)
    for ride in old_ride_data:
        # try to find the matching ride in the new ride table
        ride_info = db.find_ride_info(ride[1])
        if ride_info is not None:
            EIN_table = DB.table_name_for_EIN_ratings(ride[1])
            # columns = get_column_names_for_table('individual_ride_tables')
            columns = tuple(old_db.tables[EIN_table].keys())
            old_EIN_data = old_db.select_columns(EIN_table, columns)
            # make sure there is something in EIN table for this ride
            if old_EIN_data is not None:
                # for data in old_EIN_data:
                db.insert_many(EIN_table, columns, old_EIN_data)
                print(f'inserted {len(old_EIN_data)} to {EIN_table}')
                    # db.insert_values_for_ride_ratings(ride_name, data[:3], False)

# import aliases from old db
def import_aliases_from_old_db(db, old_db):
    cols = list(old_db.get_table_data()[DB.alias_table_name].keys())
    add_to_line = False
    old_aliases = old_db.select_columns(DB.alias_table_name, cols)
    if 'is_visible' not in cols:
        add_to_line = True
        cols += ['is_visible']
    for line in old_aliases:
        if add_to_line:
            line = list(line) + [1]
        db.insert(DB.alias_table_name, cols, line)

def generate_clean_db(db):
    # bring in the data
    generate_rides(db, True)
    generate_age_modifiers(db)
    # TODO
    # db.check_aliases()
    # print('aliases checked')

def generate_db_using_backup(db):
    DB(is_backup_db=True).backup_db(db)
    # use averages as default values
    db.set_average_values_as_default_for_all()
    # print('averages set as default EIN values')