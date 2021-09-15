
db_filename = 'rct_data.db'
ride_table_name = "rides"
age_table_name = "age_modifiers"

# create dict with columns for rides' attributes
def create_rides_columns():
    return {'name': ('TEXT', 'NOT NULL', 'UNIQUE'), 
        'rideBonusValue': ('INTEGER', 'NOT NULL'),
        'excitementValue': ('INTEGER', 'NOT NULL'),
        'intensityValue': ('INTEGER', 'NOT NULL'),
        'nauseaValue': ('INTEGER', 'NOT NULL'),
        'alias_of': ("INTEGER",),
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
