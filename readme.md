# Ride Price Calculator for OpenRCT2

Yes, this already exists at <https://rct2calc.shottysteve.com/> and probably other places. But I wanted to create my own version just because.


![Price Calculator window](pricecalculator.png)

The calculator uses kivy for its GUI. More detailed list of dependencies can be found in *requirements.txt*.

This app offers the possibility to save excitement-intensity-nausea ratings to a database, and then use the average of those ratings as default ratings. This should speed up the use of this calculator, especially when it comes to flat rides.

To launch the calculator, type

`python main.py`



### Things to maybe add

* Emphasizing the first three lines in the pricetable, as they are the most important

* Updating default ratings when saving?

* More things to manage the database better

* Making database functions less susceptible to errors

* Add missing rides (and aliases)
