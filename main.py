
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
from kivy.properties import BooleanProperty
from kivy.graphics import Color, Rectangle
# handling the RCT data and calculations
# from calc import read_ride_values, read_age_values, calculate_max_prices
from calc import get_suggestions_for_ride_name, get_EIN_value, calculate_price_table
from db_fcns import get_age_modifiers, get_ride_names, get_EIN_values_for_ride, get_default_EIN_for_ride
from modify_db import insert_values_for_ride, set_average_values_as_default


class DescriptionText(BoxLayout):
    pass


class RideTextBox(TextInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # highlight suggestions with up and down, select one with right
        if self.dropdown.parent is not None and self.suggestions[0].text != self.no_match_text:
            if keycode[1] == 'down':
                if self.active_suggestion > -1:
                    self.suggestions[self.active_suggestion].cancel_selection()
                self.active_suggestion += 1
                if self.active_suggestion == self.num_of_suggestions:
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
        # otherwise, normal behaviour
        return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def suggest_ride_names(self, widget, text):
        # if the textinput is not in focus, do nothing
        if not self.focus:
            return
        # clear dropdown just in case
        self.dropdown.clear_widgets()
        # get suggestions and place them in the dropdown
        new_sugg = get_suggestions_for_ride_name(text, self.ride_names, self.max_num_of_suggestions)
        self.num_of_suggestions = len(new_sugg)
        for i in range(self.num_of_suggestions):
            self.suggestions[i].text = new_sugg[i]
            self.dropdown.add_widget(self.suggestions[i])
        # only open dropdow if it is not already open and this TextInput is displayed
        if self.dropdown.parent is None and self.get_parent_window() is not None:
            self.dropdown.open(self)

    def select_suggestion(self, widget, value):
        if value and not(widget.text == self.no_match_text):
            self.dropdown.select(widget.text)
            # probably not necessary
            # self.dropdown.dismiss()
        # else:
        #     # is this correct?
        #     self.dropdown.select(widget.text)

    def make_selection(self, widget, value):
        self.text = value
        self.focus = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.ride_names = read_ride_values().keys()
        self.ride_names = get_ride_names()
        self.dropdown = DropDown()
        self.no_match_text = 'No match found'
        self.real_focus = False
        # max 5 suggestions
        self.max_num_of_suggestions = 5
        # at first no suggestion active
        self.active_suggestion = -1
        # readonly = True ??
        self.suggestions = [TextInput(text='', readonly=True, multiline=False, write_tab=False, size_hint_y=None, height=dp(30)) for _ in range(self.max_num_of_suggestions)]
        self.num_of_suggestions = len(self.suggestions)
        for suggestion in self.suggestions:
            suggestion.bind(focus=self.select_suggestion)
            self.dropdown.add_widget(suggestion)
            
        # self.dropdown.bind(on_select=lambda widget, value: setattr(self, 'text', value))
        self.dropdown.bind(on_select=self.make_selection)
        self.bind(text=self.suggest_ride_names)
        # self.bind(focus=self.focus_fcn)


class InputSection(GridLayout):
    free_entry_value = BooleanProperty(True)

    def set_default_EIN_values(self, ride_name):
        # if ride_name not in self.ride_name_box.ride_names:
        #     return
        default_EIN = get_default_EIN_for_ride(ride_name)
        # None is not a good default value
        if default_EIN[0] is None or default_EIN[1] is None or default_EIN[2] is None:
            return
        # set EIN values in textinputs to default
        self.excitement_value_box.text = str(default_EIN[0])
        self.intensity_value_box.text = str(default_EIN[1])
        self.nausea_value_box.text = str(default_EIN[2])

    def when_textinput_in_focus(self, widget, value):
        # close ride name dropdown if applicable
        # if widget != self.ride_name_box:
        self.close_ride_name_dropdown(widget, value)
        # highlight previous text (if any)
        if value:
            self.ride_name_box.real_focus = False
            # if no values in textinputs, set default ones
            if self.ride_name_box.text in self.ride_name_box.ride_names:
                if self.excitement_value_box.text == '' and self.intensity_value_box.text == '' and self.nausea_value_box.text == '':
                    self.set_default_EIN_values(self.ride_name_box.text)
            widget.select_all()
        
    def close_ride_name_dropdown(self, widget, value):
        if self.ride_name_box.dropdown.parent is not None and value:
            # if name is highlighted in dropdown, choose it as ride_name
            if self.ride_name_box.active_suggestion > -1:
                name = self.ride_name_box.suggestions[self.ride_name_box.active_suggestion].text
                if name != self.ride_name_box.no_match_text:
                    self.ride_name_box.text = name
                # remove highlighting
                self.ride_name_box.suggestions[self.ride_name_box.active_suggestion].cancel_selection()
                self.ride_name_box.active_suggestion = -1
            self.ride_name_box.dropdown.dismiss()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.ride_name = ''

        ride_name_label = Label(text='Select the ride type')
        self.add_widget(ride_name_label)
        self.ride_name_box = RideTextBox(text='', multiline=False, write_tab=False)
        # this does not work
        # self.ride_name_box.bind(text=self.when_textinput_in_focus)
        self.add_widget(self.ride_name_box)

        e_label = Label(text='Excitement Rating')
        self.add_widget(e_label)
        self.excitement_value_box = TextInput(text='', multiline=False, write_tab=False)
        self.add_widget(self.excitement_value_box)
        # if, ER textinput is active, close ride name suggestion dropdown
        self.excitement_value_box.bind(focus=self.when_textinput_in_focus)
        
        i_label = Label(text='Intensity Rating')
        self.add_widget(i_label)
        self.intensity_value_box = TextInput(text='', multiline=False, write_tab=False)
        self.add_widget(self.intensity_value_box)
        self.intensity_value_box.bind(focus=self.when_textinput_in_focus)

        n_label = Label(text='Nausea Rating')
        self.add_widget(n_label)
        self.nausea_value_box = TextInput(text='', multiline=False, write_tab=False)
        self.add_widget(self.nausea_value_box)
        self.nausea_value_box.bind(focus=self.when_textinput_in_focus)

        self.add_widget(Label(text='Do you charge for park entry?'))
        self.pay_for_entry_btn = ToggleButton(text='No')
        # self.pay_for_entry_btn.bind(state=self.change_pay_for_entry)
        self.add_widget(self.pay_for_entry_btn)
        

    def clear_input_boxes(self):
        self.ride_name_box.text = ''
        self.excitement_value_box.text = ''
        self.intensity_value_box.text = ''
        self.nausea_value_box.text = ''
    

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


# if len(word) < num_of_letters, add two spaces for each 'missing' letter
def add_double_spaces(word, num_of_letters):
    # if len(word) >= num_of_letters:
    #     return word
    formatted_word = word
    for _ in range(num_of_letters - len(word)):
        formatted_word += '  '
    return formatted_word

# how to show age1 - age2 as a string
def format_age_ranges(age1, age2):
    text1 = add_double_spaces(str(age1), 3)
    text2 = add_double_spaces(str(age2), 3)
    return text1 + '  ...  ' + text2


# divide by 100 and add spaces
def price_as_string(price):
    price_s = str(price)
    if price == 0:
        return '  0.00'
    if price < 100:
        return '  0.' + price_s
    if price < 1000:
        return '  ' + price_s[0] + '.' + price_s[1:]
    return price_s[:2] + '.' + price_s[2:]

# the better the price, the greener the price
# but mostly just kinda random color decisions
def price_color(price):
    # zero price is red
    if price == 0:
        return (1, 0, 0, 1)
    # turn price to a number between 0 and 100
    mult = price // 20
    # high prices are green
    if mult > 49:
        mult = (mult - 50) // 2
        return (0, 0.75 + 0.01*mult, 0, 1)
    # less green, maybe blue
    if mult > 19:
        return (0, 0.4 + 0.01*mult, 0.8 - 0.01*mult)
    # adding some red perhaps
    if mult > 4:
        return (0.4 - 0.01*mult, 0.02 * mult, 0.8 - 0.01*mult, 1)
    # more red for prices under 1 euro/dollar/etc
    mult *= 2
    return (0.9- 0.05*mult, 0, 0.4 + 0.05 * mult, 1)


class PriceTable(GridLayout):

    # background color for each row of the pricetable
    # just alternating colors for now
    def row_color(self, row_num):
        if row_num % 2 == 0:
            return (0.05, 0.05, 0.05, 1)
        return (0, 0, 0.05, 1)

    # resize boxlayout background
    def update_boxlayout(self, widget, value):
        widget.rect.pos = widget.pos
        widget.rect.size = widget.size

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.age_values = read_age_values()
        self.age_values = get_age_modifiers()
        # 12 rows, 1? + 2 + 2 columns of boxlayouts
        self.table = [BoxLayout() for _ in range(36)]
        for i, layout in enumerate(self.table):
            self.add_widget(layout)
            with layout.canvas.before:
                Color(*self.row_color(i // 3))
                layout.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(pos=self.update_boxlayout, size=self.update_boxlayout)
        # 3 labels in the first row
        cell1 = Label(text='Age (in months)')
        self.table[0].add_widget(cell1)
        cell2 = Label(text='Max Price (openRCT2)')
        self.table[1].add_widget(cell2)
        cell3 = Label(text='Max Price (classic)')
        self.table[2].add_widget(cell3)
        self.labels = [cell1, cell2, cell3]
        # 11 rows with 5 labels
        for i, layout in enumerate(self.table):
            if i > 2:
                cell = Label(text='')
                self.labels.append(cell)
                layout.add_widget(cell)
                if i % 3 != 0:
                    cell = Label(text='')
                    self.labels.append(cell)
                    layout.add_widget(cell)
        self.labels[4].text = self.labels[6].text = 'unique'
        self.labels[5].text = self.labels[7].text = 'non-unique'
        # place age ranges in the pricetable
        for i, line in enumerate(self.age_values):
            self.labels[8 + 5*i].text = format_age_ranges(line['from'], line['to'])
            # coloring the text by row seems not ideal
            # self.labels[8 + 5*i].color = self.row_color(i)

    def clear_pricetable(self):
        for i in range(len(self.age_values)):
            for j in range(1, 5):
                self.labels[8 + 5*i + j].text = ''

    def write_pricetable(self, max_prices):
        for i, priceline in enumerate(max_prices):
            for j in range(4):
                self.labels[9 + 5*i + j].text = price_as_string(priceline[j])
                self.labels[9 + 5*i + j].color = price_color(priceline[j])


class MainScreen(BoxLayout):
    
    # if clear button is pressed, clear everything
    def clear_button_pressed(self, widget):
        self.inputsection.clear_input_boxes()
        self.pricetable.clear_pricetable()

    # get excitement, intensity and nausea values from textinputs
    def get_EIN_values(self):
        excitement_str = self.inputsection.excitement_value_box.text
        intensity_str = self.inputsection.intensity_value_box.text
        nausea_str = self.inputsection.nausea_value_box.text
        # if user uses actual values
        if ('.' in excitement_str) or ('.' in intensity_str) or ('.' in nausea_str):
            excitement = get_EIN_value(excitement_str, True)
            intensity = get_EIN_value(intensity_str, True)
            nausea = get_EIN_value(nausea_str, True)
            return (excitement, intensity, nausea)
        # otherwise, we assume EIN is multiplied by 100
        excitement = get_EIN_value(excitement_str)
        intensity = get_EIN_value(intensity_str)
        nausea = get_EIN_value(nausea_str)
        return (excitement, intensity, nausea)
        
    def calculate_price(self, widget, value=None):
        ride_name = self.inputsection.ride_name_box.text.lower()
        # if ride_name is not good, do nothing
        if ride_name == '':
            return
        if ride_name not in self.inputsection.ride_name_box.ride_names:
            # should more be done here?
            return
        EIN = self.get_EIN_values()
        EIN_multipliers = get_EIN_values_for_ride(ride_name)
        max_prices = calculate_price_table(EIN_multipliers, EIN, self.pricetable.age_values, self.inputsection.free_entry_value)
        # max_prices = calculate_max_prices(self.ride_values, self.age_values, ride_name, excitement, intensity, nausea, self.inputsection.free_entry_value)
        # show the prices in the pricetable
        self.pricetable.write_pricetable(max_prices)
    
    # save EIN to the database
    def calculate_and_save(self, widget, value=None):
        ride_name = self.inputsection.ride_name_box.text.lower()
        # if ride_name is not good, do nothing
        if ride_name == '':
            return
        if ride_name not in self.inputsection.ride_name_box.ride_names:
            # should more be done here?
            return
        EIN = self.get_EIN_values()
        # ignore too low values
        if EIN[0] < 10:
            if EIN[1] < 10 and EIN[2] < 10:
                return
        insert_values_for_ride(ride_name, EIN)
        # update default values
        set_average_values_as_default(ride_name)
        # calculate prices
        EIN_multipliers = get_EIN_values_for_ride(ride_name)
        max_prices = calculate_price_table(EIN_multipliers, EIN, self.pricetable.age_values, self.inputsection.free_entry_value)
        self.pricetable.write_pricetable(max_prices)

    def ride_name_box_focus(self, widget, value):
        if value:
            if not widget.real_focus:
                widget.select_all()
            widget.real_focus = True
        if not value:
            self.calculate_price(widget)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # description of the app
        self.add_widget(DescriptionText(height=dp(75), size_hint=(0.6, None), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        # section where you input the name and ratings of your ride
        self.inputsection = InputSection(height=dp(200), size_hint=(0.8, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.inputsection)

        # buttons to clear inputs, and save ratings from input to database
        buttons = BoxLayout(size_hint=(0.6, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        # self.clear_button = Button(text='Clear', on_press=self.clear_button_pressed, size_hint=(0.1, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        buttons.add_widget(Button(text='Clear', on_press=self.clear_button_pressed, size_hint=(0.1, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        # self.calculate_button = Button(text='Calculate', on_press=self.calculate_price, size_hint=(0.1, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        buttons.add_widget(Button(text='Calculate and Save', on_press=self.calculate_and_save, size_hint=(0.1, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        self.add_widget(buttons)

        # table to show the prices
        self.pricetable = PriceTable(size_hint=(1, 1.5))
        self.add_widget(self.pricetable)

        # calculating prices automatically
        self.inputsection.ride_name_box.bind(focus=self.ride_name_box_focus)
        self.inputsection.excitement_value_box.bind(text=self.calculate_price)
        self.inputsection.intensity_value_box.bind(text=self.calculate_price)
        self.inputsection.nausea_value_box.bind(text=self.calculate_price)
        self.inputsection.pay_for_entry_btn.bind(state=self.change_pay_for_entry)

        # set focus to ride name box
        self.inputsection.ride_name_box.focus = True

    def change_pay_for_entry(self, widget, state):
        if widget.state == 'normal':
            widget.text = 'No'
            self.inputsection.free_entry_value = True
        else:
            widget.text = 'Yes'
            self.inputsection.free_entry_value = False
        self.calculate_price(widget)
    


class MainWidget(Widget):
    pass


class RCTPriceCalculatorApp(App):
    pass


if __name__ == '__main__':
    RCTPriceCalculatorApp().run()
