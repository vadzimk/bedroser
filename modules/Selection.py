from modules.PdfLine import PdfLine
from modules.func import *
from modules import PDF_CONST as PFC

class Selection:
    """ Represents area of selection on the page """
    def __init__(self, df):
        self.selection_as_line_list = convert_dataframe_tolist_of_lines(df)
        self.selection_as_dict = df.to_dict()
        self.type = None  # title_area, color_area, stock_area, packaging_area
        self.pdf_line_list = [PdfLine(line) for line in self.selection_as_line_list]

    def set_type(self, the_type=None):
        if the_type:
            self.type = the_type
        elif self.is_color_area():
            self.type = PFC.TYPE_COLOR
        elif self.is_stock_area():
            self.type = PFC.TYPE_STOCK
        elif self.is_packaging_area():
            self.type = PFC.TYPE_PACKAGING
        else:
            self.type = None

    def is_color_area(self):
        """ :return true if this is a color area """
        is_header = False
        for line in self.selection_as_line_list:
            if len(line) <= 3:
                for item in line:
                    if "Color" in str(item) or "Name Code" in str(item):
                        is_header = True
                        break
        return is_header

    def is_stock_area(self):
        """ :return true if this is a stock area """
        is_stock_area = False
        for line in self.selection_as_line_list:
            if 'Unit' in line and 'Net Price' in line:
                is_stock_area = True
                break
        return is_stock_area

    def is_packaging_area(self):
        """ :return true if this is a packaging area """
        is_packaging_area = False
        for line in self.selection_as_line_list:
            flag = False
            for item in line:
                if "Packaging Information" in str(item):
                    flag = True
                    break
            if flag:
                is_packaging_area = True
                break
        return is_packaging_area
