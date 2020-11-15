from modules.PdfLine import PdfLine

from modules.func import *
from modules import PDF_CONST as PFC
from modules.ColorArea import ColorArea

from pprint import pprint


class Selection:
    """ Represents area of selection on the page """

    def __init__(self, df, is_se):
        self.is_se = is_se
        self.selection_as_line_list = convert_dataframe_tolist_of_lines(df)
        self.selection_as_dict = df.to_dict()
        self.type = None  # title_area, color_area, stock_area, packaging_area
        self.pdf_line_list = None
        if not is_se:
            self.pdf_line_list = [PdfLine(line) for line in self.selection_as_line_list]

    def set_type(self, the_type=None):
        if the_type:
            self.type = the_type
        elif self.is_color_area():
            self.type = PFC.TYPE_COLOR
        elif self.is_categ_area():
            self.type = PFC.TYPE_CATEG
        elif self.is_stock_area():
            self.type = PFC.TYPE_STOCK
        elif self.is_packaging_area():
            self.type = PFC.TYPE_PACKAGING
        else:
            self.type = None

    def is_categ_area(self):
        is_categ = True
        for line in self.selection_as_line_list:
            if len(line) > 1:
                is_categ = False
                break
        return is_categ

    def is_color_area(self):
        """ :return true if this is a color area """
        is_header = False
        for line in self.selection_as_line_list:
            if len(line) <= 3:
                for item in line:
                    if "Color" in str(item) or "Code" in str(item):
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
                if "Packaging" in str(item) or "Packing" in str(item) or "Pcs/Ctn" in str(item):
                    flag = True
                    break
            if flag:
                is_packaging_area = True
                break
        return is_packaging_area

    def extract_color_data(self):
        """ :returns a dictionary {"Name": names, "Code": codes} containing colors of color_area"""
        color_dict = None
        condition = None
        header = self.selection_as_line_list[0]
        if len(header) == 1:
            # color table with condition
            condition = header[0].replace('Colors', '')
            condition = "".join(condition.split())
            value_lines = self.selection_as_line_list[2:]
            names = [" ".join(item[0].split()[:-1]) for item in value_lines]
            codes = [item[0].split()[-1] for item in value_lines]
            color_dict = {"Name": names, "Code": codes}
            print('color table with condition')
        elif len(header) == 2:
            # color table with condition
            if 'Colors' in header[0]:
                condition = header[0].replace('Colors', '')
                condition = "".join(condition.split())
            value_lines = self.selection_as_line_list[1:]
            names = [item[0] for item in value_lines]
            codes = [item[-1] for item in value_lines]
            color_dict = {"Name": names, "Code": codes}
        elif 'Code' in header:
            value_lines = self.selection_as_line_list[1:]
            names = [item[0] for item in value_lines]
            color_descriptions = [item[1] for item in value_lines]
            codes = [item[-1] for item in value_lines]
            color_dict = {"Name": names, "Color": color_descriptions, "Code": codes}

        print("condition:", condition)
        pprint(color_dict)

        return (color_dict, condition)

    def color_area(self):
        """ Initializes the dictionary on ColorArea object and sets its used property to false"""
        d = self.extract_color_data()
        return ColorArea(*d)

    def __str__(self):
        the_str = f"[Type: {self.type}]\n"
        for line in self.selection_as_line_list:
            line = [str(item) for item in line]
            the_str += (", ".join(line) + '\n')
        return the_str
