
# source = "C:\Pelit\Useful ride info RCT2.csv"
def read_ride_values(filepath="C:\\Pelit\\Useful ride info RCT2.csv"):
    data = []
    with open(filepath, "r") as file:
        for line in file:
            list_of_things = line.split(",")
            try:
                int(list_of_things[1])
                item = dict()
                item['ride type'] = list_of_things[0]
                item['rideBonusValue'] = int(list_of_things[1])
                item['excitementValue'] = int(list_of_things[2])
                item['intensityValue'] = int(list_of_things[3])
                item['nauseaValue'] = int(list_of_things[4])
                data.append(item)
            except ValueError:
                pass
    return data

def write_ride_values_to_file(ride_values, filepath="ride_values.csv"):
    with open(filepath, "w") as file:
        for ride in ride_values:
            line0 = (str(ride['ride type']), 
                str(ride['excitementValue']),
                str(ride['intensityValue']),
                str(ride['nauseaValue']),
                str(ride['rideBonusValue']))
            line = ','.join(line0) + ";\n"
            file.write(line)

def read_age_values(in_classic=False, filepath="C:\\Pelit\\Useful ride info RCT2.csv"):
    data = []
    with open(filepath, "r") as file:
        index = None
        reading = False
        found = False
        for line in file:
            list_of_things = line.split("\n")[0]
            if "\n" in list_of_things:
                print("onkelma")
            list_of_things = line.split(",")
            if reading and found:
                if list_of_things[index] == "":
                    reading = False
                else:
                    try:
                        second = list_of_things[index + 1]
                        if "+" in second:
                            item = (list_of_things[index], int(second), "+")
                            data.append(item)
                        else:
                            try:
                                other_item = float(second)
                                item = (list_of_things[index], other_item, "*")
                                data.append(item)
                            except ValueError:
                                pass
                    except IndexError:
                        print("jokin on vialla indeksien kanssa")
            else:
                for i, cell in enumerate(list_of_things):
                    if "Age values" in cell and not found:
                        index = i
                        reading = True
                        if not in_classic:
                            found = True
                        else:
                            in_classic = False
    return data

def get_range(range_as_string):
    items = range_as_string.split(" ")
    if len(items) > 1:
        try:
            return (int(items[0]), int(items[-1]))
        except ValueError:
            pass
    else:
        if "+" in items[0]:
            try:
                return (int(items[0][:-1]), "")
            except ValueError:
                pass

def clean_age_values(age_values):
    new_age_values = []
    # remove the header line (probably not necessary)
    # age_values = age_values[1:]
    for line in age_values:
        try:
            lower_bound, upper_bound = get_range(line[0])
            new_line = (str(lower_bound), str(upper_bound), str(line[1]), str(line[2]))
            new_age_values.append(new_line)
        except TypeError:
            pass
    return new_age_values


def write_age_values_to_file(age_values, in_classic=False):
    filename0 = "age_modifiers"
    if in_classic:
        filename = filename0 + "_classic.csv"
    else:
        filename = filename0 + ".csv"
    with open(filename, "w") as file:
        for info in age_values:
            line = ",".join(info) + ";\n"
            file.write(line)

def main():
    # save ride values to file nearby
    # ride_values = read_ride_values()
    # write_ride_values_to_file(ride_values)
    # save age values to file nearby
    age_values = read_age_values()
    age_values = clean_age_values(age_values)
    write_age_values_to_file(age_values)
    # save classic age values to file nearby
    classic_age_values = read_age_values(in_classic=True)
    classic_age_values = clean_age_values(classic_age_values)
    write_age_values_to_file(classic_age_values, in_classic=True)
    
        


if __name__ == "__main__":
    main()