from pprint import pprint

from modules import Selection


class ColorArea:
    def __init__(self, thedict, cond):
        self.color_dict = thedict
        self.condition = cond # for conditional colors or None
        self.length = len(list(thedict.values())[0])
        self.used = False  # a flag that is changed to true after the stock area finished processing and next type of area comes in

    def __str__(self):
        pprint(self.color_dict)




