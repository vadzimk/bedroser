import functools

import pandas

import modules.PDF_CONST as PFC
from modules import PROJ_CONST as PR
from modules.PdfLine import PdfLine
from modules.Selection import Selection
import csv
from pprint import pprint


class PageProductTable:
    """ contains products in a dictionary """

    def __init__(self, page_number, selection_dfs):
        self._selection_dfs = selection_dfs
        self.selection_objects = [Selection(df) for df in selection_dfs]
        self.set_selection_types()  # init selection types
        self._pagenumber = page_number
        # self.lines = lines
        # print("guessed_rows")
        # for row in guessed_rows:
        #     print(row)
        # self.guessed_rows_strings = [self.join_list_items(item) for item in
        #                              guessed_rows]  # joins guessed rows and retrurns a list of strings
        # print("guessed_strings:")
        # for string in self.guessed_rows_strings:
        #     print(string)
        # # print("---tabulalines:")
        # # for line in lines:
        # #     print(line._tabula_line)
        # print("__ end")
        self.colors = None  # for testing

        self.__products = {key: [] for key in
                           PFC.PRODUCT_TABLE_FIELDS}  # dictionary that will hold the items of the table
        #  fields of the csv data frame:
        self._series_name = None
        self._group = None
        self._subgroup = None  # subgroup is like "BULLNOSE"
        self._vendor_code = None
        self._item_size = None
        self._item_color = None
        self._units_per_carton = None  # after testing change default value to 1
        self._units_of_measure = None
        self._unit_price = None

        # supplemental properties
        self.color_areas = []  # contains Color_area objects that are pushed as the build_table is running
        self.packaging_selections = self.collect_packaging_selections()  # a list of Packaging_selection objects of current page that is fixed by the time  build_table is called
        self.group_prefix = ''  # represents category prefix of subgroup

        # print("num pack sel", len(self.packaging_selections))

        self.build_table()  # put products in the dictionary

        # TODO keep this
        # export product table as csv
        # df = pandas.DataFrame(self.__products)
        # df.to_csv('{}data_frame{}.csv'.format(PR.DIR_PRODUCT_TABLES, page_number), index=False)

        # # export treated rows as csv
        # self.export_treated_rows()

    def build_table(self):
        print("build_table:")

        for area in self.selection_objects:
            print(area)

            if area.type == PFC.TYPE_TITLE:
                for line in area.pdf_line_list:
                    self._series_name = line.find_series_name() if line.find_series_name() else self._series_name
            elif area.type == PFC.TYPE_COLOR:
                self.color_areas.append(area.color_area())
            # TODO ============== working on this part ==============
            elif area.type == PFC.TYPE_STOCK:
                for line in area.pdf_line_list:
                    if line.is_group_prefix_row():
                        self.group_prefix = line.find_group_prefix()
                        continue   # don not push attributes to the dictionary - continue to the next iteration
                    if line._is_product_table_row:
                        self._group = self.group_prefix + ' ' + line.find_group() if line.find_group() else self._group
                        self._subgroup = line.find_subgroup() if line.find_subgroup() else self._subgroup
                        self._item_size = line.find_item_size() if line.find_item_size() else self._item_size
                        self._units_of_measure = line.find_units_of_measure() if line.find_units_of_measure() else self._units_of_measure
                        self._unit_price = line.find_unit_price() if line.find_unit_price() else self._unit_price

                        # extract packaging data for the item in STOCK area

                        for selection in self.packaging_selections:
                            for packaging_line in selection.pdf_line_list:
                                u_p_c = packaging_line.find_units_per_carton(self._subgroup, self._item_size)
                                self._units_per_carton = u_p_c if u_p_c else self._units_per_carton

                        item_code = line.find_vendor_code() if line.find_vendor_code() else self._vendor_code
                        chr = u'\u25CF'
                        if not chr in item_code:
                            self._vendor_code = item_code
                            self.push_attributes()

                        # self._item_color = line.find_item_color() if line.find_item_color() else self._item_color
                        #
                        # multiplier = functools.reduce(lambda a, b: a.length + b.length, self.color_areas)
                        # multiplier = multiplier if multiplier > 0 else 1
                        # print("multiplier", multiplier)

                        # todo --- find all attributes for the line
                        # todo --- iterate over packaging information and attach packaging data
                        # todo --- iterate over color dictionary and push this line necessary number of times to the cumulative dict

        print("Attributes:")
        print(self._series_name)
        print(self._group)
        print(self._subgroup)
        print(self._item_size)
        print(self._units_of_measure)
        print(self._unit_price)
        print(self._units_per_carton)

        # for item in area.selection_as_dict.keys():
        #     if

        # todo p 42 contains many color areas and packaging info on the next page!
        # todo: move the
        #    #  represent selections as lists of lines
        #         self.selections_as_line_lists = self.convert_list_of_dataframes_to_selection_lines(self.selection_dataframes)
        #
        #  todo ; to the Pageproduct table to manipulate
        #  todo ; areas are sorted thus can be processed successively
        #  todo ; for each area in the page
        #  todo ; pass current_area to create a list of PdfLines and extract relevant properties

        """ sees what fields are detected by the PdfLine and builds product table"""
        # for line in self.lines:  # line comes form fixed column recognition
        #
        #     """not TODO skip lines that are not valid, check if line is guessed list if so than it is valid, """
        #     cur_line_string = self.join_list_items(line._tabula_line)
        #     valid_line = False
        #     # for item in self.guessed_rows_strings:
        #     #     if item in cur_line_string:
        #     #         valid_line = True
        #     if cur_line_string in self.guessed_rows_strings or (
        #             'Units' in cur_line_string and 'Price' in cur_line_string):
        #         valid_line = True
        #
        #     if valid_line:  # line matches the auto guessed row
        #         """collect the fields"""
        #         self._series_name = line.find_series_name() if line.find_series_name() else self._series_name
        #         self._group = line.find_group() if line.find_group() else self._group
        #         self._subgroup = line.find_subgroup() if line.find_subgroup() else self._subgroup
        #         self._vendor_code = line.find_vendor_code() if line.find_vendor_code() else self._vendor_code
        #         self._item_size = line.find_item_size() if line.find_item_size() else self._item_size
        #         self._item_color = line.find_item_color() if line.find_item_color() else self._item_color
        #         self._units_per_carton = line.find_units_per_carton() if line.find_units_per_carton() else self._units_per_carton
        #         self._units_of_measure = line.find_units_of_measure() if line.find_units_of_measure() else self._units_of_measure
        #         self._unit_price = line.find_unit_price() if line.find_unit_price() else self._unit_price
        #
        #         multiplier = 1  # number of times the row must be multiplied
        #         if self.colors:  # if color list is present, a product row will be appended the number of colors times
        #             multiplier = len(self.colors)

        #         if line._is_product_table_row and self._series_name:
        #             # print("is_product_table_row: ", line._is_product_table_row)
        #             # print("_series_name", self._series_name)
        #
        #             """push properties to the dictionary"""
        #             for i in range(multiplier):
        #                 for key in PFC.PRODUCT_TABLE_FIELDS:
        #                     if self.colors and key == "_item_color":
        #                         value = self.colors[i]
        #                     else:
        #                         value = eval("self.%s" % (key))  # line at key
        #                     self.__products[key].append(value)
        #
        #     # print(valid_line, cur_line_string)

    def get_products(self):
        """@:returns the dictionary of products representing product table of the page"""
        return self.__products

    # def export_treated_rows(self):
    #     """ export treated rows as csv"""
    #     frame = []
    #     for line in self.lines:
    #         frame.append(line._row)
    #     with open("{}treated{}.csv".format(PR.DIR_TREATED_ROWS, self._pagenumber), "w", newline='') as f:
    #         wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    #         wr.writerows(frame)

    def join_list_items(self, list_obj):
        line_string_list = [str(item) for item in list_obj]  # strignify any non-string types of items of the list
        line_string = "".join(line_string_list)  # join all items in one string (with no spaces between items)
        line_string = "".join(line_string.split())
        return line_string

    def set_selection_types(self):
        # initialize selection's type:
        self.selection_objects[0].set_type(PFC.TYPE_TITLE)  # set the first area to title area
        # set remaining areas
        for i in range(1, len(self.selection_objects)):
            self.selection_objects[i].set_type()

    def collect_packaging_selections(self):
        """ :return a list of packaging selections of the current page"""
        packaging_selections = []
        for selection in self.selection_objects:
            if selection.type == PFC.TYPE_PACKAGING:
                packaging_selections.append(selection)
        return packaging_selections

    def push_attributes(self, multiplier=1):
        """push properties to the dictionary"""
        for i in range(multiplier):
            for key in PFC.PRODUCT_TABLE_FIELDS:
                if self.colors and key == "_item_color":
                    value = self.colors[i]
                else:
                    value = eval("self.%s" % (key))  # line at key
                self.__products[key].append(value)
