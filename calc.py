
def read_ride_values():
    ride_values = []
    with open("ride_values.csv", "r") as file:
        for line in file:
            dataline0 = line.split(";")[0]
            dataline = dataline0.split(",")
            ride = dict()
            ride['rideType'] = dataline[0]
            ride['excitementValue'] = int(dataline[1])
            ride['intensityValue'] = int(dataline[2])
            ride['nauseaValue'] = int(dataline[3])
            ride['rideBonusValue'] = int(dataline[4])
            ride_values.append(ride)
    return ride_values

# just consider integers
def read_age_values():
    age_values = []
    with open("age_modifiers.csv", "r") as file:
        for line in file:
            dataline0 = line.split(";")[0]
            if dataline0 == "":
                break
            dataline = dataline0.split(",")
            age_value = {"from": int(dataline[0])}
            try:
                age_value['to'] = int(dataline[1])
            except ValueError:
                age_value['to'] = ""
            age_value['modifier_type'] = dataline[3]
            age_value['modifier'] = int(100 * float(dataline[2]))
            age_values.append(age_value)
    with open("age_modifiers_classic.csv", "r") as file:
        for i, line in enumerate(file):
            dataline0 = line.split(";")[0]
            if dataline0 == "":
                break
            dataline = dataline0.split(",")
            age_values[i]['modifier_type_classic'] = dataline[3]
            if dataline[3] == "*":
                age_values[i]['modifier_classic'] = int(100* float(dataline[2]))
            else:
                age_values[i]['modifier_classic'] = int(dataline[2])
    return age_values

def add_empty_space_at_the_end(word, length):
    if len(word) < length:
        new_word = word
        for _ in range(length - len(word)):
            new_word = new_word + " "
        return new_word
    return word

def rounding(num):
    return int((num // 10) // 10 * 10)

def maximize(num):
    return 2 * num - 10

# EIN as integers (i.e. multiplied by 100)
def calculate_max_price(ride_type, excitement, intensity, nausea, free_entry=True):
    ride_values = read_ride_values()
    age_values = read_age_values()
    for ride in ride_values:
        if ride['rideType'].lower() == ride_type.lower():
            e_multiplier = ride['excitementValue']
            i_multiplier = ride['intensityValue']
            n_multiplier = ride['nauseaValue']
            break
    else:
        print("Cannot find ride of type", ride_type)
        return
    ride_value = (excitement * e_multiplier) // 1024 + (intensity * i_multiplier) // 1024 + (nausea * n_multiplier) // 1024
    max_prices = []
    for age in age_values:
        price_unique = maximize(rounding(ride_value * age['modifier']))
        
        price = maximize(rounding(((3 * ride_value / 4) // 1) * age['modifier']))
        if age['modifier_type_classic'] == "*":
            price_unique_c = maximize(rounding(ride_value * age['modifier_classic']))
            price_c = maximize(rounding((int(3 * ride_value / 4)) * age['modifier_classic']))
        else:
            # print(ride_value * age['modifier'] // 100, ride_value + age['modifier_classic'])
            price_unique_c = maximize(rounding(100 * (ride_value + age['modifier_classic'])))
            price_c = maximize(rounding(300 * (ride_value + age['modifier_classic']) / 4))
        max_prices.append((price_unique, price, price_unique_c, price_c))
    # if also pay-for-entry, prices are quarter of that of free entry
    if not free_entry:
        new_max_prices = []
        for price_line in max_prices:
            new_price_line = []
            for price in price_line:
                price = price // 4
                price = price // 10 * 10
                new_price_line.append(price)
            new_max_prices.append(tuple(new_price_line))
        max_prices = new_max_prices
    return max_prices

def calculator():
    ride_name = input("What is the ride type? ")
    print("Type the rating values of the ride without dots, i.e. multiplied by 100.")
    excitement = int(input("Excitement rating of the ride: "))
    intensity = int(input("Intensity rating of the ride: "))
    nausea = int(input("Nausea rating of the ride: "))
    ans = input("Do you also charge for park entry? ")
    if ans.lower() == "yes" or ans.lower() == "y":
        free_entry = False
    else:
        free_entry = True
    max_prices = calculate_max_price(ride_name, excitement, intensity, nausea, free_entry)
    print("\nThese are the maximum prices you can charge, depending on the age of the ride.\n")
    print("Age\t", "Max price (openRCT2)", "Max price (classic)", sep="\t")
    age_values = read_age_values()
    for i, price_line in enumerate(max_prices):
        from_ = add_empty_space_at_the_end(str(age_values[i]['from']), 3)
        to_ = add_empty_space_at_the_end(str(age_values[i]['to']), 3)
        print(from_ + " ... " + to_ + "\t", *price_line, sep="\t")




if __name__ == "__main__":
    calculator()
