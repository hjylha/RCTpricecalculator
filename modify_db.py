from os import stat
from db_setup import create_default_EIN_columns, create_EIN_columns, ride_table_name, create_rides_columns
from db_stuff import create_table, insert_data, select_all, select_rows_by_column_value, update_data_by_rowid, insert_data_and_create_table_if_not_created
from db_fcns import get_ride_names, find_ride_info, get_ride_rowid
import statistics


# saving EIN values to db
# table name = 'ein' + str(rowid) (of the original ride, not aliases)
def get_table_name_for_ride(ride_name):
    ride_info = find_ride_info(ride_name)
    if ride_info[ride_name]['alias_of'] is not None:
        return str(ride_info[ride_name]['alias_of'])
    return 'ein' + str(ride_info[ride_name]['ride_id'])

def create_table_for_ride(ride_name):
    table_name = get_table_name_for_ride(ride_name)
    columns = create_EIN_columns()
    create_table(table_name, columns)

def insert_values_for_ride(ride_name, EIN):
    table_name = get_table_name_for_ride(ride_name)
    columns = create_EIN_columns()
    insert_data_and_create_table_if_not_created(table_name, columns, EIN)
    

# add a new ride to the ride table
def add_ride(ride_data):
    columns = create_rides_columns().keys()
    insert_data(ride_table_name, columns, ride_data)

def update_ride_values(ride_data):
    pass

# set new default/average values for EIN
def update_default_values(ride_name, new_default_EIN):
    rowid = get_ride_rowid(ride_name)
    EIN_columns = create_default_EIN_columns()
    update_data_by_rowid(ride_table_name, EIN_columns, new_default_EIN, rowid)

# calculate average EIN ratings
def calculate_average_EIN(ride_name):
    table = get_table_name_for_ride(ride_name)
    all_data = select_all(table)
    e_values, i_values, n_values = [], [], []
    for data in all_data:
        e_values.append(data[1])
        i_values.append(data[2])
        n_values.append(data[3])
    e_average = statistics.mean(e_values)
    i_average = statistics.mean(i_values)
    n_average = statistics.mean(n_values)
    return (e_average, i_average, n_average)

# calculate average EIN and set them as default
def set_average_values_as_default(ride_name):
    average_EIN = calculate_average_EIN(ride_name)
    update_default_values(ride_name, average_EIN)

# add new row to ride table, which is a duplicate of an old row except for the name
def add_alias(new_ride_name, old_ride_name):
    columns = create_rides_columns.keys()
    old_data = select_rows_by_column_value(ride_table_name, 'name', old_ride_name.lower())
    alias_of = old_data[0]
    new_data = old_data[1:]
    # alias has the same stats, except name and reference to the original
    new_data[0] = new_ride_name.lower()
    new_data[5] = alias_of
    insert_data(ride_table_name, columns, new_data)

# add new rides, update values or add aliases
def modify_db():
    pass


if __name__ == '__main__':
    modify_db()
