from db_setup import create_age_columns, DB
from get_data import read_age_values, read_ride_values
# from pathlib import Path


# using game files to generate database is currently done in db_setup.py
# def generate_rides_from_game_files(openrct_path):
#     pass   

# def generate_age_modifiers_from_game_files(openrct_path):
#     pass


# create tables: rides, age_modifiers
# and fill them with data
def generate_rides_from_csv_file():
    db = DB(DB.db_filename)
    rides_columns = DB.create_rides_columns()
    db.create_table(DB.ride_table_name, rides_columns)
    ride_values = read_ride_values()
    columns = ('name', 'rideBonusValue', 'excitementValue', 'intensityValue', 'nauseaValue')
    for ride in ride_values:
        data = [ride_values[ride][column] for column in columns[1:]]
        data.insert(0, ride)
        db.insert(DB.ride_table_name, columns, data)
        # print('inserted', data)

def generate_age_modifiers_from_csv_file():
    db = DB(DB.db_filename)
    age_columns = create_age_columns()
    db.create_table(DB.age_table_name, age_columns)
    age_values = read_age_values()
    for age in age_values:
        data = [age[column] for column in list(age_columns.keys())[2:]]
        if age['to'] != '':
            data.insert(0, age['to'])
        else:
            data.insert(0, None)
        data.insert(0, age['from'])
        db.insert(DB.age_table_name, age_columns, data)
        # print('inserted', age)

# generate both tables
def generate_tables_from_csv_files(make_rides=True, make_age=True):
    # generate ride value table
    if make_rides:
        generate_rides_from_csv_file()
    # generate age value table
    if make_age:
        generate_age_modifiers_from_csv_file()


def show_all():
    db = DB(DB.db_filename)
    ride_values = db.select_all(DB.ride_table_name)
    for ride in ride_values:
        print(ride)
    age_modifiers = db.select_all(DB.age_table_name)
    for age in age_modifiers:
        print(age)


if __name__ == '__main__':
    # with open('openrct_path.txt', 'r') as f:
    #     openrct_path = Path(f.readline().strip())
    db = DB(DB.db_filename)
    db.generate_clean_db()
    # generate_tables_from_csv_files()
