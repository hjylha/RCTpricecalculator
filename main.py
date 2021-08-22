from kivy.app import App
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.dropdown import DropDown
from kivy.properties import BooleanProperty, StringProperty

from calc import read_ride_values, read_age_values, calculate_max_prices, add_empty_space_at_the_end
from calc import get_suggestions_for_ride_name


class DescriptionText(BoxLayout):
    pass

class RideTextBox(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # print(self.dropdown.parent, self)
        if self.dropdown.parent is not None and self.suggestions[0].text != "No match found":
            if keycode[1] == 'down':
                if self.active_suggestion > -1:
                    self.suggestions[self.active_suggestion].cancel_selection()
                self.active_suggestion += 1
                if self.active_suggestion == len(self.suggestions):
                    self.active_suggestion = -1
                elif self.active_suggestion > -1:
                    self.suggestions[self.active_suggestion].select_all()
                return True
            elif keycode[1] == 'up':
                if self.active_suggestion > -1:
                    self.suggestions[self.active_suggestion].cancel_selection()
                    self.active_suggestion -= 1
                    if self.active_suggestion > -1:
                        self.suggestions[self.active_suggestion].select_all()
                return True
            elif keycode[1] == 'right':
                if self.active_suggestion > -1:
                    self.suggestions[self.active_suggestion].cancel_selection()
                    self.text = self.suggestions[self.active_suggestion].text
                    self.active_suggestion = -1
            
        return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def suggest_ride_names(self, widget, text):
        # if the textinput is not in focus, do nothing
        if not self.focus:
            return
        
        # clear dropdown just in case
        self.dropdown.clear_widgets()
        new_sugg = get_suggestions_for_ride_name(text, self.ride_names, self.num_of_suggestions)
        for i in range(len(new_sugg)):
            self.suggestions[i].text = new_sugg[i]
            self.dropdown.add_widget(self.suggestions[i])
        

        # only open DropDown if it is not already open and this TextInput is displayed
        if self.dropdown.parent is None and self.get_parent_window() is not None:
            # print("opening dropdown")
            self.dropdown.open(self)

    def select_suggestion(self, widget, value):
        # print("suggestion")
        # print(widget, "has value", value)
        if value and not(widget.text == "No match found"):
            self.dropdown.select(widget.text)
            # probably not necessary
            # self.dropdown.dismiss()
        # else:
        #     # is this correct?
        #     self.dropdown.select(widget.text)

    def make_selection(self, widget, value):
        # print("selected")
        # print(widget)
        # print(value)
        self.text = value
        self.focus = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ride_names = read_ride_values().keys()
        self.dropdown = DropDown()
        # 5 suggestions
        self.num_of_suggestions = 5
        # at first no suggestion active
        self.active_suggestion = -1
        # readonly = True ??
        self.suggestions = [TextInput(text="", readonly=True, multiline=False, write_tab=False, size_hint_y=None, height=dp(30)) for _ in range(self.num_of_suggestions)]
        for suggestion in self.suggestions:
            suggestion.bind(focus=self.select_suggestion)
            self.dropdown.add_widget(suggestion)
            
        # self.dropdown.bind(on_select=lambda widget, value: setattr(self, 'text', value))
        self.dropdown.bind(on_select=self.make_selection)
        self.bind(text=self.suggest_ride_names)


# def on_text(instance, value):
#     print("The widget", instance, "has:", value)
#     return value

# def on_text2(instance, value):
#     print("(2) Widget", instance, "has:", value)
#     return value

class InputSection(GridLayout):
    # ride_name = StringProperty("")
    # excitement_value = StringProperty("")
    # intensity_value = StringProperty("")
    # nausea_value = StringProperty("")
    free_entry_value = BooleanProperty(True)

    # widget = textinput, value = text
    def suggest_ride_names(self, widget, value):
        # if the textinput is not in focus, do nothing
        if not widget.focus:
            return
        # get suggestions from somewhere
        # suggestions = ["Junior Coaster", "Giga Coaster", "Go Karts", "Observation Tower", "Steel Wild Mouse"]
        suggestions = ["No match found"]
        
        for i, suggestion in enumerate(suggestions):
            # btn = Button(text=suggestion, size_hint_y=None, height=dp(30))
            # btn.bind(on_release=lambda btn: self.ride_name_box.dropdown.select(btn.text))
            # self.ride_name_box.dropdown.add_widget(btn)
            widget.suggestions[i].text = suggestion
        # only open DropDown if it is not already open and this TextInput is displayed
        if widget.dropdown.parent is None and widget.get_parent_window() is not None:
            # print("opening dropdown")
            self.ride_name_box.dropdown.open(self.ride_name_box)
        
    def close_ride_name_dropdown(self, widget, value):
        if self.ride_name_box.dropdown.parent is not None and value:
            # if name is highlighted in dropdown, choose it as ride_name
            if self.ride_name_box.active_suggestion > -1:
                name = self.ride_name_box.suggestions[self.ride_name_box.active_suggestion].text
                self.ride_name_box.text = name
                # remove highlighting
                self.ride_name_box.suggestions[self.ride_name_box.active_suggestion].cancel_selection()
                self.ride_name_box.active_suggestion = -1
            self.ride_name_box.dropdown.dismiss()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ride_names = read_ride_values().keys()
        self.ride_name = ""
        # self.excitement_value = ""
        # self.intensity_value = ""
        # self.nausea_value = ""
        # self.free_entry = True

        ride_name_label = Label(text="Select the ride type")
        self.add_widget(ride_name_label)
        self.ride_name_box = RideTextBox(text="", multiline=False, write_tab=False)
        # try to suggest correct ride names
        # self.ride_name_box.bind(text=self.suggest_ride_names)
        self.add_widget(self.ride_name_box)
        # self.suggestions = []
        # # 5 suggestions
        # for _ in range(5):
        #     btn = Button(text="", size_hint_y=None, height=dp(30))
        #     btn.bind(on_release=lambda btn: self.ride_name_box.dropdown.select(btn.text))
        #     self.ride_name_box.dropdown.add_widget(btn)
        #     self.suggestions.append(btn)

        e_label = Label(text="Excitement Rating")
        self.add_widget(e_label)
        self.excitement_value_box = TextInput(text="", multiline=False, write_tab=False)
        self.add_widget(self.excitement_value_box)
        self.excitement_value_box.bind(focus=self.close_ride_name_dropdown)
        
        i_label = Label(text="Intensity Rating")
        self.add_widget(i_label)
        self.intensity_value_box = TextInput(text="", multiline=False, write_tab=False)
        self.add_widget(self.intensity_value_box)
        # self.intensity_value_box.bind(focus=self.close_ride_name_dropdown)

        n_label = Label(text="Nausea Rating")
        self.add_widget(n_label)
        self.nausea_value_box = TextInput(text="", multiline=False, write_tab=False)
        self.add_widget(self.nausea_value_box)
        # self.nausea_value_box.bind(focus=self.close_ride_name_dropdown)

        self.add_widget(Label(text="Do you charge for park entry?"))
        self.pay_for_entry_btn = ToggleButton(text="No")
        # self.pay_for_entry_btn.bind(state=self.change_pay_for_entry)
        self.add_widget(self.pay_for_entry_btn)
        

    def clear_input_boxes(self):
        self.ride_name_box.text = ""
        self.excitement_value_box.text = ""
        self.intensity_value_box.text = ""
        self.nausea_value_box.text = ""

    # def get_input_data(self):
    #     return (self.ride_name_box.text.lower(), self.excitement_value_box.text)

    # def change_pay_for_entry(self, widget, state):
    #     if widget.state == "normal":
    #         widget.text = "No"
    #         self.free_entry_value = True
    #     else:
    #         widget.text = "Yes"
    #         self.free_entry_value = False
    
    

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
    

    def clear_button_pressed(self, widget):
        self.inputsection.clear_input_boxes()
        self.inputsection.ride_name = ""
        self.excitement = 0
        self.intensity = 0
        self.nausea = 0
        self.pricetable.clear_pricetable()
        
    def calculate_price(self, widget, value=None):
        ride_name = self.inputsection.ride_name_box.text.lower()
        # if ride_name is not good, do nothing
        if ride_name == "":
            return
        if ride_name not in self.ride_values.keys():
            # should more be done here?
            # dropdown = DropDown()
            # self.inputsection.ride_name_box.add_widget(dropdown)
            # dropdown.add_widget(Label(text="No match found"))
            return
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
        # for priceline in max_prices:
        #     print(priceline)

    def ride_name_box_focus(self, widget, value):
        if not value:
            self.calculate_price(widget)
        # if value:
        #     # suggestions, maybe?
        #     # print("writing in", widget)
        #     pass
        # else:
        #     # close the dropdown
        #     print(self.inputsection.excitement_value_box.focus)
        #     other_input_active = self.inputsection.excitement_value_box.focus or self.inputsection.intensity_value_box.focus or self.inputsection.nausea_value_box.focus

        #     if self.inputsection.ride_name_box.dropdown.parent is not None and other_input_active:
        #         self.inputsection.ride_name_box.dropdown.dismiss()
        #     self.calculate_price(widget)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ride_name = ""
        # self.excitement = 0
        # self.intensity = 0
        # self.nausea = 0
        # self.free_entry = True
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

        # calculating prices automatically
        self.inputsection.ride_name_box.bind(focus=self.ride_name_box_focus)
        self.inputsection.excitement_value_box.bind(text=self.calculate_price)
        self.inputsection.intensity_value_box.bind(text=self.calculate_price)
        self.inputsection.nausea_value_box.bind(text=self.calculate_price)
        self.inputsection.pay_for_entry_btn.bind(state=self.change_pay_for_entry)

    def change_pay_for_entry(self, widget, state):
        if widget.state == "normal":
            widget.text = "No"
            self.inputsection.free_entry_value = True
        else:
            widget.text = "Yes"
            self.inputsection.free_entry_value = False
        self.calculate_price(widget)
    


class MainWidget(Widget):
    pass

class RCTPriceCalculatorApp(App):
    pass

if __name__ == "__main__":
    RCTPriceCalculatorApp().run()
