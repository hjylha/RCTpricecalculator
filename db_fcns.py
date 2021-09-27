# # This file seems to be currently useless

# import statistics
# from db_setup import db_filename, ride_table_name, age_table_name, create_rides_columns, create_EIN_columns, create_default_EIN_columns, table_for_EIN_ratings
# from db_stuff import DB_general


# # get the list of ride names in the db
# def get_ride_names():
#     db = DB_general(db_filename)
#     names0 = db.select_columns(ride_table_name, ('name',))
#     return [name[0] for name in names0]

# # get age modifiers in the same form as before
# def get_age_modifiers():
#     db = DB_general(db_filename)
#     age_modifiers = []
#     age_modifiers0 = db.select_all(age_table_name)
#     for age in age_modifiers0:
#         age_modifier = {'from': age[1]}
#         if age[2] is not None:
#             age_modifier['to'] = age[2]
#         else:
#             age_modifier['to'] = ''
#         age_modifier['modifier_type'] = age[3]
#         age_modifier['modifier'] = age[4]
#         age_modifier['modifier_type_classic'] = age[5]
#         age_modifier['modifier_classic'] = age[6]
#         age_modifiers.append(age_modifier)
#     return age_modifiers

# # test if name is unique
# def find_rides(ride_name):
#     db = DB_general(db_filename)
#     rides = db.select_rows_by_column_value(ride_table_name, 'name', ride_name.lower())
#     return rides

# # we assume that name is unique, since that is a restriction we have placed
# def find_ride_info(ride_name):
#     db = DB_general(db_filename)
#     rides = db.select_rows_by_column_value(ride_table_name, 'name', ride_name.lower())
#     # if len(rides) == 1:
#     ride = rides[0]
#     return {ride_name: ride[1], 
#             'excitementValue': ride[3],
#             'intensityValue': ride[4],
#             'nauseaValue': ride[5],
#             'alias_of': ride[6],
#             'defaultExcitement': ride[7],
#             'defaultIntensity': ride[8],
#             'defaultNausea': ride[9],
#             'rideBonusValue': ride[2],
#             'ride_id': ride[0]}

# # just get the rowid of the row containing ride
# def get_ride_rowid(ride_name):
#     ride_info = find_ride_info(ride_name)
#     return ride_info['ride_id']

# def get_EIN_values_for_ride(ride_name):
#     ride_info = find_ride_info(ride_name)
#     return (ride_info['excitementValue'], ride_info['intensityValue'], ride_info['nauseaValue'])

# def get_default_EIN_for_ride(ride_name):
#     ride_info = find_ride_info(ride_name)
#     return (ride_info['defaultExcitement'], ride_info['defaultIntensity'], ride_info['defaultNausea'])


# # saving EIN values to db
# # table name = 'ein' + str(rowid) (of the original ride, not aliases)
# def get_table_for_ride_ratings(ride_name):
#     return table_for_EIN_ratings(get_ride_rowid(ride_name))

# def create_table_for_ride_ratings(ride_name):
#     db = DB_general(db_filename)
#     table_name = get_table_for_ride_ratings(ride_name)
#     columns = create_EIN_columns()
#     db.create_table(table_name, columns)

# def insert_values_for_ride_ratings(ride_name, EIN):
#     db = DB_general(db_filename)
#     table_name = get_table_for_ride_ratings(ride_name)
#     columns = create_EIN_columns()
#     db.insert_and_create_table_if_needed(table_name, columns, EIN)

# # set new default/average values for EIN
# def update_default_values(ride_name, new_default_EIN):
#     db = DB_general(db_filename)
#     rowid = get_ride_rowid(ride_name)
#     EIN_columns = create_default_EIN_columns()
#     db.update_by_rowid(ride_table_name, EIN_columns, new_default_EIN, rowid)

# # calculate average EIN ratings
# def calculate_average_EIN(ride_name):
#     db = DB_general(db_filename)
#     table = get_table_for_ride_ratings(ride_name)
#     all_data = db.select_all(table)
#     # in case of errors, return nothing
#     if all_data is None:
#         return None
#     e_values, i_values, n_values = [], [], []
#     for data in all_data:
#         e_values.append(data[1])
#         i_values.append(data[2])
#         n_values.append(data[3])
#     e_average = int(statistics.mean(e_values))
#     i_average = int(statistics.mean(i_values))
#     n_average = int(statistics.mean(n_values))
#     return (e_average, i_average, n_average)

# # calculate average EIN and set them as default
# def set_average_values_as_default(ride_name):
#     average_EIN = calculate_average_EIN(ride_name)
#     if average_EIN is not None:
#         update_default_values(ride_name, average_EIN)
#     else:
#         print(ride_name, 'does not have recorded ratings')

# # do averaging for all rides
# def set_average_values_as_default_for_all():
#     ride_names = get_ride_names()
#     for ride in ride_names:
#         set_average_values_as_default(ride)


# # add a new ride to the ride table
# def add_ride(ride_data):
#     db = DB_general(db_filename)
#     columns = create_rides_columns().keys()
#     db.insert_data(ride_table_name, columns, ride_data)

# # not sure if more general updates are necessary
# def update_ride_values(ride_data):
#     pass



# # add new row to ride table, which is a duplicate of an old row except for the name
# # maybe make a new table for aliases instead????????????
# def add_alias(new_ride_name, old_ride_name):
#     db = DB_general(db_filename)
#     columns = create_rides_columns.keys()
#     old_data = db.select_rows_by_column_value(ride_table_name, 'name', old_ride_name.lower())
#     alias_of = old_data[0]
#     new_data = old_data[1:]
#     # alias has the same stats, except name and reference to the original
#     new_data[0] = new_ride_name.lower()
#     new_data[5] = alias_of
#     db.insert_data(ride_table_name, columns, new_data)