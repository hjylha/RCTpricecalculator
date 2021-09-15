from db_setup import ride_table_name, age_table_name
import db_stuff as db

def get_ride_names():
    names0 = db.select_columns(ride_table_name, ('name',))
    return [name[0] for name in names0]

# get age modifiers in the same form as before
def get_age_modifiers():
    age_modifiers = []
    age_modifiers0 = db.select_all(age_table_name)
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

# test if name is unique
def find_rides(ride_name):
    rides = db.select_rows_by_column_value(ride_table_name, 'name', ride_name.lower())
    return rides

# we assume that name is unique, since that is a restriction we have placed
def find_ride_info(ride_name):
    rides = db.select_rows_by_column_value(ride_table_name, 'name', ride_name.lower())
    # if len(rides) == 1:
    ride = rides[0]
    return {ride_name: {'excitementValue': ride[3],
                        'intensityValue': ride[4],
                        'nauseaValue': ride[5],
                        'alias_of': ride[6],
                        'defaultExcitement': ride[7],
                        'defaultIntensity': ride[8],
                        'defaultNausea': ride[9],
                        'rideBonusValue': ride[2]}}

def get_EIN_values_for_ride(ride_name):
    ride_info = find_ride_info(ride_name)
    return (ride_info[ride_name]['excitementValue'], ride_info[ride_name]['intensityValue'], ride_info[ride_name]['nauseaValue'])

def get_default_EIN_for_ride(ride_name):
    ride_info = find_ride_info(ride_name)
    return (ride_info[ride_name]['defaultExcitement'], ride_info[ride_name]['defaultIntensity'], ride_info[ride_name]['defaultNausea'])

