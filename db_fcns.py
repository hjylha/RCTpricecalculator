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


