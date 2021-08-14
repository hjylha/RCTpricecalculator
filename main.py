from kivy.app import App
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, StringProperty

from calc import read_ride_values, read_age_values, calculate_max_prices, add_empty_space_at_the_end


class DescriptionText(BoxLayout):
    pass

def on_text(instance, value):
    print("The widget", instance, "has:", value)
    return value

def on_text2(instance, value):
    print("(2) Widget", instance, "has:", value)
    return value

class InputSection(GridLayout):
    ride_name = StringProperty("")
    excitement_value = StringProperty("")
    intensity_value = StringProperty("")
    nausea_value = StringProperty("")
    free_entry_value = BooleanProperty(True)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ride_name = "Placeholder"
        # self.excitement_value = ""
        # self.intensity_value = ""
        # self.nausea_value = ""
        # self.free_entry = True

        ride_name_label = Label(text="Select the ride type")
        self.add_widget(ride_name_label)
        self.ride_name_box = TextInput(text="", multiline=False, write_tab=False)
        # bind seems to not do anything useful for me
        # self.ride_name_box.bind(text=on_text)
        self.add_widget(self.ride_name_box)

        e_label = Label(text="Excitement Rating")
        self.add_widget(e_label)
        self.excitement_value_box = TextInput(text="", multiline=False, write_tab=False)
        self.add_widget(self.excitement_value_box)
        
        i_label = Label(text="Intensity Rating")
        self.add_widget(i_label)
        self.intensity_value_box = TextInput(text="", multiline=False, write_tab=False)
        self.add_widget(self.intensity_value_box)

        n_label = Label(text="Nausea Rating")
        self.add_widget(n_label)
        self.nausea_value_box = TextInput(text="", multiline=False, write_tab=False)
        self.add_widget(self.nausea_value_box)
        

    def clear_input_boxes(self):
        self.ride_name_box.text = ""
        self.excitement_value_box.text = ""
        self.intensity_value_box.text = ""
        self.nausea_value_box.text = ""

    def get_input_data(self):
        return (self.ride_name_box.text.lower(), self.excitement_value_box.text)

    def change_pay_for_entry(self, widget):
        if widget.state == "normal":
            widget.text = "No"
            self.free_entry_value = True
        else:
            widget.text = "Yes"
            self.free_entry_value = False
        
        # test
        # print(self)
        # print(self.get_input_data())
        # self.clear_input_boxes()
        # if self.free_entry_value:
        #     print("park has free entry")
        # else:
        #     print("park is pay-for-entry")
    
    

# class RideSelection(BoxLayout):
#     pass

# class ExcitementSelection(BoxLayout):
#     pass

# class IntensitySelection(BoxLayout):
#     pass

# class NauseaSelection(BoxLayout):
#     pass

# class PayForEntrySelection(BoxLayout):
#     pass

# class Buttons(BoxLayout):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)


class PriceTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.age_values = read_age_values()
        # 12 rows, 3 columns
        cell1 = Label(text="Age")
        self.add_widget(cell1)
        cell2 = Label(text="Max Price (openRCT2)")
        self.add_widget(cell2)
        cell3 = Label(text="Max Price (classic)")
        self.add_widget(cell3)
        self.labels = [cell1, cell2, cell3]
        for _ in range(33):
            cell = Label(text="")
            self.labels.append(cell)
            self.add_widget(cell)
        self.labels[4].text = "unique - - - non-unique"
        self.labels[5].text = "unique - - - non-unique"
        age_values = read_age_values()
        for i, line in enumerate(age_values):
            start_age = add_empty_space_at_the_end(str(line['from']), 3)
            end_age = add_empty_space_at_the_end(str(line['to']), 3)
            text_to_cell = start_age + " ... " + end_age
            self.labels[3 * (i + 2)].text = text_to_cell

    def clear_pricetable(self):
        for i in range(len(self.age_values)):
            self.labels[3 * (i + 2) + 1].text = ""
            self.labels[3 * (i + 2) + 2].text = ""

    def write_pricetable(self, max_prices):
        for i, priceline in enumerate(max_prices):
            text1 = str(priceline[0]) + " - - - " + str(priceline[1])
            text2 = str(priceline[2]) + " - - - " + str(priceline[3])
            self.labels[3 * (i + 2) + 1].text = text1
            self.labels[3 * (i + 2) + 2].text = text2


class MainScreen(BoxLayout):
    
    # pricetable = PriceTable(cols=3, padding=(dp(0), dp(20), dp(0), dp(20)))

    def clear_button_pressed(self, widget):
        self.inputsection.clear_input_boxes()
        self.inputsection.ride_name = ""
        self.excitement = 0
        self.intensity = 0
        self.nausea = 0
        self.pricetable.clear_pricetable()
        
    def calculate_price(self, widget):
        ride_name = self.inputsection.ride_name_box.text
        try:
            excitement = int(self.inputsection.excitement_value_box.text)
        except ValueError:
            excitement = 0
        try:
            intensity = int(self.inputsection.intensity_value_box.text)
        except ValueError:
            intensity = 0
        try:
            nausea = int(self.inputsection.nausea_value_box.text)
        except ValueError:
            nausea = 0
        max_prices = calculate_max_prices(self.ride_values, self.age_values, ride_name, excitement, intensity, nausea, self.inputsection.free_entry_value)

        self.pricetable.write_pricetable(max_prices)
        for priceline in max_prices:
            print(priceline)

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.inputsection = InputSection()
        # self.pricetable = PriceTable()
        # test if it works
        # print(self.pricetable.labels[0].text)
        self.ride_name = ""
        self.excitement = 0
        self.intensity = 0
        self.nausea = 0
        self.free_entry = True
        self.ride_values = read_ride_values()
        self.age_values = read_age_values()

        self.add_widget(DescriptionText(height=dp(75), size_hint=(0.6, None), pos_hint={"center_x": 0.5, "center_y": 0.5}))
        self.inputsection = InputSection(height=dp(200), size_hint=(0.8, None), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.add_widget(self.inputsection)

        buttons = BoxLayout(size_hint=(0.6, 0.2), pos_hint={"center_x": 0.5, "center_y": 0.5})
        # self.clear_button = Button(text="Clear", on_press=self.clear_button_pressed, size_hint=(0.1, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})
        buttons.add_widget(Button(text="Clear", on_press=self.clear_button_pressed, size_hint=(0.1, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5}))
        # self.calculate_button = Button(text="Calculate", on_press=self.calculate_price, size_hint=(0.1, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})
        buttons.add_widget(Button(text="Calculate", on_press=self.calculate_price, size_hint=(0.1, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5}))
        self.add_widget(buttons)

        self.pricetable = PriceTable(size_hint=(1, 1.5))
        self.add_widget(self.pricetable)

        # self.inputsection.ride_name_box.bind(text=on_text2)

    


class MainWidget(Widget):
    pass

class RCTPriceCalculatorApp(App):
    pass

RCTPriceCalculatorApp().run()
