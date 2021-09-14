from db_stuff import create_table, insert_data, select_all
from calc import read_age_values, read_ride_values


# create dict with columns for rides' attributes
def create_rides_columns():
    return {'name': ('TEXT', 'NOT NULL', 'UNIQUE'), 
        'rideBonusValue': ('INTEGER', 'NOT NULL'),
        'excitementValue': ('INTEGER', 'NOT NULL'),
        'intensityValue': ('INTEGER', 'NOT NULL'),
        'nauseaValue': ('INTEGER', 'NOT NULL'),
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
        


# create tables: rides, age_modifiers
# and fill them with data
def generate_rides():
    table_name = 'rides'
    rides_columns = create_rides_columns()
    create_table(table_name, rides_columns)
    ride_values = read_ride_values()
    columns = ('name', 'rideBonusValue', 'excitementValue', 'intensityValue', 'nauseaValue')
    for ride in ride_values:
        columns = ('name', 'rideBonusValue', 'excitementValue', 'intensityValue', 'nauseaValue')
        data = [ride_values[ride][column] for column in columns[1:]]
        data.insert(0, ride)
        insert_data(table_name, columns, data)

def generate_age_modifiers():
    table_name = 'age_modifiers'
    age_columns = create_age_columns()
    create_table(table_name, age_columns)
    age_values = read_age_values()
    for age in age_values:
        data = [age[column] for column in list(age_columns.keys())[2:]]
        if age['to'] != '':
            data.insert(0, age['to'])
        else:
            data.insert(0, None)
        data.insert(0, age['from'])
        # print(age_columns.keys())
        # print(data)
        insert_data(table_name, age_columns, data)
        # print('inserted', age)

# generate both tables
def generate_tables(make_rides=True, make_age=True):
    # generate ride value table
    if make_rides:
        generate_rides()
    # generate age value table
    if make_age:
        generate_age_modifiers()


def show_all():
    ride_values = select_all('rides')
    for ride in ride_values:
        print(ride)
    age_modifiers = select_all('age_modifiers')
    for age in age_modifiers:
        print(age)


if __name__ == '__main__':
    generate_tables()
