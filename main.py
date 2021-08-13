from kivy.app import App
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty

from calc import read_ride_values, read_age_values, calculate_max_prices, add_empty_space_at_the_end


class DescriptionText(BoxLayout):
    pass

class InputSection(GridLayout):
    free_entry_value = BooleanProperty(True)

    def change_pay_for_entry(self, widget):
        if widget.state == "normal":
            widget.text = "No"
            self.free_entry_value = True
        else:
            widget.text = "Yes"
            self.free_entry_value = False
        # test
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

class PriceTable(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        pass


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputsection = InputSection()
        self.pricetable = PriceTable()
        # test if it works
        # print(self.pricetable.labels[0].text)
        self.ride_name = ""
        self.excitement = 0
        self.intensity = 0
        self.nausea = 0
        self.free_entry = True

    def clear_button_pressed(self):
        print("you have pressed the clear button")


class MainWidget(Widget):
    pass

class RCTPriceCalculatorApp(App):
    pass

RCTPriceCalculatorApp().run()
